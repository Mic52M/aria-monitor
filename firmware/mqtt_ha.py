# Integrazione Home Assistant via MQTT Discovery.
# Richiede umqtt.simple (lo installiamo con mip, vedi README).
import json

try:
    from umqtt.simple import MQTTClient
except ImportError:
    MQTTClient = None


class HomeAssistant:
    def __init__(self, cfg):
        self.cfg = cfg
        self.client = None
        self.dev_id = cfg.DEVICE_NAME.replace("-", "_")
        self.base = "aria/{}".format(self.dev_id)   # topic di stato
        self.available = False

    def connect(self):
        if MQTTClient is None:
            return False
        self.client = MQTTClient(
            client_id=self.dev_id,
            server=self.cfg.MQTT_HOST,
            port=self.cfg.MQTT_PORT,
            user=self.cfg.MQTT_USER,
            password=self.cfg.MQTT_PASSWORD,
            keepalive=60,
        )
        self.client.set_last_will(self.base + "/availability", b"offline", retain=True)
        self.client.connect()
        self.client.publish(self.base + "/availability", b"online", retain=True)
        self.available = True
        self._publish_discovery()
        return True

    def _device_block(self):
        return {
            "identifiers": [self.dev_id],
            "name": self.cfg.DEVICE_NAME,
            "manufacturer": "DIY",
            "model": "ESP32 + SCD41",
        }

    def _discovery_one(self, key, name, unit, device_class):
        topic = "homeassistant/sensor/{}_{}/config".format(self.dev_id, key)
        payload = {
            "name": name,
            "unique_id": "{}_{}".format(self.dev_id, key),
            "state_topic": self.base + "/state",
            "value_template": "{{ value_json.%s }}" % key,
            "unit_of_measurement": unit,
            "device_class": device_class,
            "state_class": "measurement",
            "availability_topic": self.base + "/availability",
            "device": self._device_block(),
        }
        self.client.publish(topic, json.dumps(payload), retain=True)

    def _publish_discovery(self):
        self._discovery_one("co2", "CO2", "ppm", "carbon_dioxide")
        self._discovery_one("temperature", "Temperatura", "°C", "temperature")
        self._discovery_one("humidity", "Umidita", "%", "humidity")

    def publish_state(self, co2, temp, rh):
        if not self.available:
            return
        payload = json.dumps({
            "co2": co2,
            "temperature": round(temp, 1),
            "humidity": round(rh, 1),
        })
        try:
            self.client.publish(self.base + "/state", payload)
        except Exception:
            self.available = False
