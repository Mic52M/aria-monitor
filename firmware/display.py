# Wrapper per display OLED SSD1306 128x64 su I2C.
# Richiede il modulo ssd1306.py (lo installiamo con mip, vedi README).
try:
    import ssd1306
except ImportError:
    ssd1306 = None


class Display:
    def __init__(self, i2c, width=128, height=64):
        self.oled = None
        if ssd1306 is not None:
            try:
                self.oled = ssd1306.SSD1306_I2C(width, height, i2c)
            except Exception:
                self.oled = None

    def show(self, co2, temp, rh, status):
        if self.oled is None:
            return
        o = self.oled
        o.fill(0)
        o.text("Aria Monitor", 0, 0)
        o.text("CO2: {} ppm".format(co2), 0, 16)
        o.text("Temp: {:.1f}C".format(temp), 0, 28)
        o.text("Umid: {:.0f}%".format(rh), 0, 40)
        o.text(status, 0, 54)
        o.show()

    def message(self, *lines):
        if self.oled is None:
            return
        o = self.oled
        o.fill(0)
        for i, line in enumerate(lines[:6]):
            o.text(str(line), 0, i * 10)
        o.show()
