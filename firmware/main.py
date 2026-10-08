# Aria Monitor - loop principale.
import time
from machine import Pin, I2C

import config as cfg
import wifi
from scd41 import SCD41
from display import Display
import telegram
import email_alert

# --- I2C: adatta i pin alla tua board (ESP32-S3 Qwiic tipico: SDA=8, SCL=9) ---
I2C_SDA = 8
I2C_SCL = 9
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=100000)

disp = Display(i2c)
disp.message("Aria Monitor", "avvio...")

# --- Sensore (opzionale: se assente si va in modalita' test) ---
sensor = None
if 0x62 in i2c.scan():
    try:
        sensor = SCD41(i2c)
        sensor.stop()                  # assicura stato pulito
        sensor.set_altitude(cfg.ALTITUDE_M)
        sensor.set_temperature_offset(getattr(cfg, "TEMP_OFFSET_C", 4.0))
        sensor.start()
        print("SCD41 trovato")
    except Exception as e:
        print("SCD41 init KO:", e)
        sensor = None
else:
    print("SCD41 non presente -> modalita' TEST (WiFi + display + dashboard)")

# --- WiFi ---
ip = None
try:
    disp.message("WiFi...", cfg.WIFI_SSID)
    static = None
    if getattr(cfg, "USE_STATIC_IP", False):
        static = (cfg.STATIC_IP, cfg.SUBNET, cfg.GATEWAY, cfg.DNS)
    ip = wifi.connect(cfg.WIFI_SSID, cfg.WIFI_PASSWORD, cfg.DEVICE_NAME, static=static)
    print("IP:", ip)
    disp.message("WiFi OK", ip)
except Exception as e:
    print("WiFi KO:", e)
    disp.message("WiFi KO", str(e))

# --- Web server ---
web = None
try:
    from webserver import WebServer
    web = WebServer(cfg)
except Exception as e:
    print("Web KO:", e)

# --- Home Assistant (MQTT) ---
ha = None
if cfg.MQTT_ENABLED:
    try:
        from mqtt_ha import HomeAssistant
        ha = HomeAssistant(cfg)
        ha.connect()
        print("MQTT/HA connesso")
    except Exception as e:
        print("MQTT KO:", e)

if ip:
    telegram.send(cfg, "Aria Monitor online. Dashboard: http://{}".format(ip))
    email_alert.send(cfg, "Aria Monitor online",
                     "Il monitor e' acceso. Dashboard: http://{}".format(ip))


def classify(co2):
    if co2 >= cfg.CO2_ALARM:
        return "AERARE SUBITO!"
    if co2 >= cfg.CO2_WARN:
        return "Aria da rinnovare"
    return "Aria buona"


last_measure = 0
alarm_sent = False

while True:
    now = time.time()

    if sensor is None and now - last_measure >= cfg.MEASURE_INTERVAL:
        # Modalita' test: nessun sensore, mostra placeholder e servi la dashboard
        status = "in attesa sensore"
        disp.show(0, 0.0, 0.0, status)
        if web:
            web.update(0, 0.0, 0.0, status)
        last_measure = now

    if sensor is not None and now - last_measure >= cfg.MEASURE_INTERVAL and sensor.data_ready():
        r = sensor.read()
        if r:
            co2, temp, rh = r
            co2 = int(co2)
            status = classify(co2)
            print(co2, "ppm", round(temp, 1), "C", round(rh), "%", "-", status)

            disp.show(co2, temp, rh, status)
            if web:
                web.update(co2, temp, rh, status)
            if ha:
                ha.publish_state(co2, temp, rh)

            # Notifica Telegram con isteresi (una volta per superamento soglia)
            if co2 >= cfg.CO2_ALARM and not alarm_sent:
                msg = "CO2 alta: {} ppm - apri la finestra!".format(co2)
                telegram.send(cfg, msg)
                email_alert.send(cfg, "Aria Monitor: CO2 alta ({} ppm)".format(co2), msg)
                alarm_sent = True
            elif co2 < cfg.CO2_WARN:
                alarm_sent = False

            last_measure = now

    if web:
        web.poll()
    time.sleep_ms(50)
