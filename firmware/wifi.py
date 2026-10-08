import network
import time


def connect(ssid, password, hostname="aria-monitor", timeout=20, static=None):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    try:
        wlan.config(dhcp_hostname=hostname)
    except Exception:
        pass
    if static:
        try:
            wlan.ifconfig(static)   # (ip, subnet, gateway, dns)
        except Exception as e:
            print("IP statico KO:", e)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        t0 = time.time()
        while not wlan.isconnected():
            if time.time() - t0 > timeout:
                raise OSError("WiFi timeout")
            time.sleep_ms(200)
    return wlan.ifconfig()[0]   # ritorna l'IP
