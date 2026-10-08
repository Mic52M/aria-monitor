# Driver minimale per Sensirion SCD41 (CO2 / temperatura / umidita') in MicroPython.
# Comunicazione I2C, indirizzo 0x62.
import time

_ADDR = 0x62

# Comandi (16 bit, big-endian)
_CMD_START_PERIODIC   = b"\x21\xb1"
_CMD_READ_MEAS        = b"\xec\x05"
_CMD_STOP_PERIODIC    = b"\x3f\x86"
_CMD_DATA_READY       = b"\xe4\xb8"
_CMD_SET_ALTITUDE     = b"\x24\x27"
_CMD_SET_TEMP_OFFSET  = b"\x24\x1d"
_CMD_REINIT           = b"\x36\x46"


def _crc8(data):
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x31) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


class SCD41:
    def __init__(self, i2c):
        self.i2c = i2c

    def _send(self, cmd, arg=None):
        buf = bytearray(cmd)
        if arg is not None:
            hi = (arg >> 8) & 0xFF
            lo = arg & 0xFF
            buf += bytes([hi, lo, _crc8(bytes([hi, lo]))])
        self.i2c.writeto(_ADDR, buf)

    def stop(self):
        self._send(_CMD_STOP_PERIODIC)
        time.sleep_ms(500)

    def set_altitude(self, meters):
        # Va impostata mentre la misura periodica e' ferma.
        self._send(_CMD_SET_ALTITUDE, int(meters))
        time.sleep_ms(1)

    def set_temperature_offset(self, celsius):
        # Offset di temperatura (default fabbrica 4C). Alza -> temperatura riportata piu' bassa.
        # Va impostato a misura ferma. Corregge anche l'umidita'.
        val = int(celsius * 65535 / 175)
        self._send(_CMD_SET_TEMP_OFFSET, val)
        time.sleep_ms(1)

    def start(self):
        self._send(_CMD_START_PERIODIC)
        time.sleep_ms(1)

    def data_ready(self):
        self._send(_CMD_DATA_READY)
        time.sleep_ms(1)
        raw = self.i2c.readfrom(_ADDR, 3)
        val = (raw[0] << 8) | raw[1]
        # pronto se gli ultimi 11 bit non sono tutti 0
        return (val & 0x07FF) != 0

    def read(self):
        """Ritorna (co2_ppm, temp_c, umidita_pct) oppure None se CRC errato."""
        self._send(_CMD_READ_MEAS)
        time.sleep_ms(1)
        d = self.i2c.readfrom(_ADDR, 9)
        # 3 word: [co2, crc][temp, crc][rh, crc]
        for i in range(0, 9, 3):
            if _crc8(d[i:i+2]) != d[i+2]:
                return None
        co2 = (d[0] << 8) | d[1]
        t_raw = (d[3] << 8) | d[4]
        rh_raw = (d[6] << 8) | d[7]
        temp = -45 + 175 * (t_raw / 65535)
        rh = 100 * (rh_raw / 65535)
        return co2, temp, rh
