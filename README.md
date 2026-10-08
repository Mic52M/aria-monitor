# Aria Monitor 🌬️

A small, always-on **indoor air-quality monitor** built on an ESP32-S3 and a Sensirion SCD41 CO₂ sensor, written in MicroPython. It shows live CO₂, temperature and humidity on an OLED screen, serves a responsive web dashboard on the local network, and sends an email when the air needs refreshing.

![Wiring diagram](wiring-diagram.svg)

## About this project

My day-to-day work is software. **This is my first hardware / embedded project** — my first time with microcontrollers, I²C buses, breadboards and soldering — so I picked something small enough to finish end to end but real enough to use every day: a device that tells me when a room has become stuffy.

## Why CO₂?

In a closed room, CO₂ rises with every breath. Above roughly 1000 ppm many people notice drowsiness and reduced concentration; outdoor air sits near 420 ppm. CO₂ is a handy proxy for "this room is not being ventilated", so a live reading makes it obvious when to open a window.

## Features

- 📟 **OLED display** with live CO₂, temperature, humidity and a status line
- 🌐 **Web dashboard** (mobile friendly): colour-coded CO₂, trend sparkline, auto-refresh every 5 s and a manual "refresh" button
- 📬 **Email alerts** via the [Resend](https://resend.com) API when CO₂ crosses a threshold (with hysteresis, so one alert per episode instead of a flood)
- 🏠 **Home Assistant** integration through MQTT auto-discovery (optional)
- 📲 Optional Telegram notifications
- 📌 **Static IP** support so the dashboard always lives at the same address
- 🌡️ Configurable **temperature offset** to compensate for the sensor's self-heating
- 🧪 Runs without the sensor attached (test mode) to verify Wi-Fi, display and dashboard first

## Hardware

| Part | Model | Notes |
|---|---|---|
| Microcontroller | ESP32-S3-DevKitC-1 (N16R8, external antenna) | Wi-Fi + BLE, USB-C |
| CO₂ sensor | Sensirion **SCD41** breakout | CO₂ + temperature + humidity over I²C (`0x62`) |
| Display | 0.96" **SSD1306** OLED, 128×64 | I²C (`0x3C`) |
| Prototyping | Solderless breadboard + Dupont jumper wires | The sensor header needed a few solder joints |

Both peripherals share one I²C bus, so the breadboard is used to fan the four shared lines out to both devices.

### Wiring

| ESP32-S3 | SCD41 | OLED |
|---|---|---|
| `3V3` | `VDD` | `VCC` |
| `GND` | `GND` | `GND` |
| `GPIO8` (SDA) | `SDA` | `SDA` |
| `GPIO9` (SCL) | `SCL` | `SCL` |

⚠️ Power both modules from **3V3**, not 5 V. SDA/SCL pins are set by `I2C_SDA` / `I2C_SCL` in `firmware/main.py`.

## Project layout

```
firmware/
  boot.py            runs at startup
  main.py            main loop: measure → display → dashboard → MQTT → alerts
  config.example.py  settings template (copy to config.py)
  scd41.py           SCD41 driver (I²C commands, CRC-8 checking, altitude and temperature offset)
  display.py         SSD1306 OLED wrapper
  wifi.py            Wi-Fi connection, optional static IP
  webserver.py       non-blocking HTTP server: dashboard + /data JSON endpoint
  mqtt_ha.py         Home Assistant MQTT discovery
  email_alert.py     email alerts via Resend
  telegram.py        optional Telegram alerts
flash.sh             flashes MicroPython onto the board
deploy.sh            installs libraries and uploads the firmware
wiring-diagram.svg   wiring overview
```

## Getting started

### 1. Install the tooling
```bash
pip install esptool mpremote
```

### 2. Flash MicroPython
Download the **ESP32_GENERIC_S3** `.bin` from <https://micropython.org/download/ESP32_GENERIC_S3/> into the project folder (named `micropython-esp32s3-*.bin`), put the board in download mode (hold **BOOT**, tap **RST**), then:
```bash
./flash.sh
```
After flashing, tap **RST** once so the board boots into MicroPython.

### 3. Configure
```bash
cp firmware/config.example.py firmware/config.py
```
Edit `firmware/config.py`: Wi-Fi credentials, the Resend API key and recipient address, thresholds, and (optionally) a static IP. `config.py` is git-ignored — secrets never leave your machine.

### 4. Deploy
```bash
./deploy.sh
```
This installs `ssd1306`, `umqtt.simple` and `urequests` on the board, copies the firmware, and reboots it.

### 5. Open the dashboard
Watch the boot log with `mpremote repl` to see the IP address, then open `http://<device-ip>/` in a browser on the same network. The raw readings are available as JSON at `/data`.

## Configuration highlights

| Setting | Purpose |
|---|---|
| `CO2_WARN` / `CO2_ALARM` | Yellow state / red state and email trigger (ppm) |
| `TEMP_OFFSET_C` | Sensor temperature offset; raise it if the reading is too warm |
| `ALTITUDE_M` | Altitude compensation for CO₂ accuracy |
| `USE_STATIC_IP`, `STATIC_IP`, `GATEWAY`, … | Fixed address for the dashboard |
| `EMAIL_ENABLED`, `RESEND_API_KEY`, `EMAIL_TO` | Email alerts |
| `MQTT_ENABLED` | Home Assistant discovery |

Suggested CO₂ bands: < 1000 ppm good · 1000–1200 ppm mediocre · > 1200 ppm ventilate.

## Things I learned along the way

- **ESP32-S3 over native USB:** the chip doesn't always reset cleanly after flashing; a manual tap on **RST** is needed before `mpremote` can connect, and the first flash needs the BOOT + RST download-mode sequence.
- **esptool v5** renamed its subcommands (`erase-flash`, `write-flash`).
- **MicroPython sockets can send partial buffers.** My first dashboard truncated its own JavaScript because `send()` accepted only part of the page. The server now loops until every byte is out and sends a `Content-Length` header.
- **The SCD41 reads a few degrees warm** because of board self-heating; the offset register on the sensor corrects both temperature and derived humidity.
- **I²C scan first:** `i2c.scan()` returning `[60, 98]` (OLED + SCD41) is the fastest way to prove the wiring and the solder joints before debugging software.

## Roadmap

- [ ] Persistent history (flash file or InfluxDB/Grafana)
- [ ] CO₂ forced recalibration outdoors (~420 ppm)
- [ ] 3D-printed enclosure
- [ ] Battery operation with deep sleep

## License

MIT
