#!/usr/bin/env bash
# Flash MicroPython onto an ESP32-S3 connected over USB.
set -e
PORT=$(ls /dev/cu.usbmodem* /dev/cu.wchusbserial* /dev/cu.usbserial* /dev/cu.SLAB_USBtoUART 2>/dev/null | head -1)
if [ -z "$PORT" ]; then echo "❌ ESP32 not found. Plug in a USB-C *data* cable and retry."; exit 1; fi
echo "✓ ESP32 found on $PORT"
BIN=$(ls -t micropython-esp32s3-*.bin 2>/dev/null | head -1)
if [ -z "$BIN" ]; then echo "❌ Put the MicroPython .bin in this folder (micropython-esp32s3-*.bin)."; exit 1; fi
echo "→ Erasing flash..."
python3 -m esptool --chip esp32s3 --port "$PORT" erase-flash
echo "→ Writing MicroPython ($BIN)..."
python3 -m esptool --chip esp32s3 --port "$PORT" write-flash 0 "$BIN"
echo "✅ MicroPython installed. Tap RST once, then run: ./deploy.sh"
