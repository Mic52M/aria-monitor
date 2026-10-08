# Copy this file to `config.py` and fill in your own values.
# config.py is git-ignored: never commit real credentials.

# --- Wi-Fi ---
WIFI_SSID = "YOUR_WIFI"
WIFI_PASSWORD = "YOUR_PASSWORD"

# --- Device identity ---
DEVICE_NAME = "aria-livingroom"      # used for the MQTT topic and DHCP hostname

# --- MQTT / Home Assistant (optional) ---
MQTT_ENABLED = False
MQTT_HOST = "192.168.1.10"           # broker address (often the Home Assistant host)
MQTT_PORT = 1883
MQTT_USER = "mqtt_user"
MQTT_PASSWORD = "mqtt_pass"

# --- Telegram alerts (optional) ---
TELEGRAM_ENABLED = False
TELEGRAM_BOT_TOKEN = "123456:ABC-DEF..."   # from @BotFather
TELEGRAM_CHAT_ID = "123456789"

# --- Email alerts via Resend ---
EMAIL_ENABLED = False
RESEND_API_KEY = "re_xxxxxxxxxxxx"
EMAIL_FROM = "Aria Monitor <onboarding@resend.dev>"  # use a verified domain for other recipients
EMAIL_TO = "you@example.com"

# --- CO2 thresholds (ppm) ---
CO2_WARN = 1000     # air getting stale (yellow)
CO2_ALARM = 1200    # ventilate now (red) + alert

# --- Measurement interval (seconds) ---
# The SCD41 in periodic mode produces a new sample about every 5 s.
MEASURE_INTERVAL = 5

# --- Altitude compensation for the CO2 sensor (metres above sea level) ---
ALTITUDE_M = 100

# --- Network: static IP so the dashboard is always at the same address ---
USE_STATIC_IP = False
STATIC_IP = "192.168.1.222"
SUBNET = "255.255.255.0"
GATEWAY = "192.168.1.1"
DNS = "192.168.1.1"

# --- Temperature calibration (deg C). Higher = lower reported temperature. Factory default is 4.0 ---
TEMP_OFFSET_C = 4.0
