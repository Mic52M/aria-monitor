#!/usr/bin/env bash
# Install the libraries and upload the firmware to the board.
set -e
cd "$(dirname "$0")/firmware"
if [ ! -f config.py ]; then echo "ERROR: copy config.example.py to config.py and fill it in first."; exit 1; fi
if grep -q 'YOUR_WIFI' config.py; then echo "ERROR: set your Wi-Fi credentials in firmware/config.py first."; exit 1; fi
echo "Installing libraries on the device..."
mpremote mip install ssd1306
mpremote mip install umqtt.simple
mpremote mip install urequests
echo "Copying firmware..."
mpremote cp config.py scd41.py wifi.py display.py mqtt_ha.py telegram.py email_alert.py webserver.py main.py boot.py :
echo "Rebooting..."
mpremote reset
echo "Done. Watch the logs with: mpremote repl (exit with Ctrl-])"
