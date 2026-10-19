# Aria Monitor - main application loop.
import time
from machine import Pin, I2C

import config as cfg
import wifi
from scd41 import SCD41
from display import Display
import telegram
import email_alert

# --- I2C: adjust the pins to your board (default wiring: SDA=GPIO8, SCL=GPIO9) ---
I2C_SDA = 8
I2C_SCL = 9
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=100000)

disp = Display(i2c)
disp.message("Aria Monitor", "starting...")

# --- Sensor (optional: when absent, the device runs in test mode) ---
sensor = None
if 0x62 in i2c.scan():
    try:
        sensor = SCD41(i2c)
        sensor.stop()                  # make sure we start from a clean state
        sensor.set_altitude(cfg.ALTITUDE_M)
        sensor.set_temperature_offset(getattr(cfg, "TEMP_OFFSET_C", 4.0))
        sensor.start()
        print("SCD41 found")
    except Exception as e:
        print("SCD41 init failed:", e)
        sensor = None
else:
    print("SCD41 not found -> TEST mode (Wi-Fi + display + dashboard only)")

# --- Wi-Fi ---
ip = None
try:
    disp.message("Wi-Fi...", cfg.WIFI_SSID)
    static = None
    if getattr(cfg, "USE_STATIC_IP", False):
        static = (cfg.STATIC_IP, cfg.SUBNET, cfg.GATEWAY, cfg.DNS)
    ip = wifi.connect(cfg.WIFI_SSID, cfg.WIFI_PASSWORD, cfg.DEVICE_NAME, static=static)
    print("IP:", ip)
    disp.message("Wi-Fi OK", ip)
except Exception as e:
    print("Wi-Fi failed:", e)
    disp.message("Wi-Fi failed", str(e))

# --- Web server ---
web = None
try:
    from webserver import WebServer
    web = WebServer(cfg)
except Exception as e:
    print("Web server failed:", e)

# --- Home Assistant (MQTT) ---
ha = None
if cfg.MQTT_ENABLED:
    try:
        from mqtt_ha import HomeAssistant
        ha = HomeAssistant(cfg)
        ha.connect()
        print("MQTT / Home Assistant connected")
    except Exception as e:
        print("MQTT failed:", e)

if ip:
    telegram.send(cfg, "Aria Monitor online. Dashboard: http://{}".format(ip))
    email_alert.send(cfg, "Aria Monitor online",
                     "The monitor is online. Dashboard: http://{}".format(ip))


def classify(co2):
    if co2 >= cfg.CO2_ALARM:
        return "VENTILATE NOW!"
    if co2 >= cfg.CO2_WARN:
        return "Air getting stale"
    return "Air is good"


last_measure = 0
alarm_sent = False

while True:
    now = time.time()

    if sensor is None and now - last_measure >= cfg.MEASURE_INTERVAL:
        # Test mode: no sensor, show a placeholder and keep serving the dashboard
        status = "Awaiting sensor"
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

            # Alerts use hysteresis: one notification per threshold crossing
            if co2 >= cfg.CO2_ALARM and not alarm_sent:
                msg = "High CO2: {} ppm - open a window!".format(co2)
                telegram.send(cfg, msg)
                email_alert.send(cfg, "Aria Monitor: high CO2 ({} ppm)".format(co2), msg)
                alarm_sent = True
            elif co2 < cfg.CO2_WARN:
                alarm_sent = False

            last_measure = now

    if web:
        web.poll()
    time.sleep_ms(50)
