#!/usr/bin/env bash
# Install libraries and upload the firmware to the board.
set -e
cd "$(dirname "$0")/firmware"
if [ ! -f config.py ]; then echo "⚠️  Copy config.example.py to config.py and fill it in first."; exit 1; fi
if grep -q 'IL_TUO_WIFI\|YOUR_WIFI' config.py; then echo "⚠️  Set your Wi-Fi credentials in firmware/config.py first."; exit 1; fi
echo "→ Installing libraries on the device..."
mpremote mip install ssd1306
mpremote mip install umqtt.simple
mpremote mip install urequests
echo "→ Copying firmware..."
mpremote cp config.py scd41.py wifi.py display.py mqtt_ha.py telegram.py email_alert.py webserver.py main.py boot.py :
echo "→ Rebooting..."
mpremote reset
echo "✅ Deployed. Watch the logs with:  mpremote repl   (exit with Ctrl-])"
