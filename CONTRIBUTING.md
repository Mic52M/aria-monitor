# Contributing

Thanks for your interest in Aria Monitor. Bug reports, hardware compatibility notes and pull requests are all welcome.

## Reporting issues

Please include:

- your board and sensor models, and how they are wired
- the MicroPython version (`import sys; sys.version` in the REPL)
- the output of `i2c.scan()` and the relevant boot log from `mpremote repl`
- what you expected and what happened

Never paste your `config.py`, API keys or Wi-Fi credentials into an issue.

## Development setup

```bash
pip install esptool mpremote
cp firmware/config.example.py firmware/config.py   # fill in your own values
./flash.sh      # first time only
./deploy.sh     # upload after every change
mpremote repl   # watch the logs
```

The firmware also runs without the SCD41 attached (test mode), which is handy for working on the dashboard or the display.

## Guidelines

- Keep modules small and single-purpose, in the style of the existing files.
- The device has limited RAM: avoid large allocations and keep the main loop non-blocking.
- Handle hardware and network failures without crashing the loop; a missing display or a failed email must never stop measurements.
- Keep user-facing text, comments and documentation in English.
- Never commit secrets. `firmware/config.py` is git-ignored; only `config.example.py` is tracked.
- Check that every file compiles before opening a pull request: `python3 -m py_compile firmware/*.py`.

## Pull requests

1. Fork the repository and create a topic branch.
2. Make focused commits with clear messages.
3. Describe what changed and how you tested it on hardware (board, sensor, MicroPython version).
4. Update the README if you change behaviour, configuration or wiring.

By contributing, you agree that your contributions are licensed under the MIT License.
