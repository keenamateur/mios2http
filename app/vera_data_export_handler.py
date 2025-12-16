# vera_data_export_handler.py

import paho.mqtt.client as mqtt
import json
import logging
import threading
import time
from config import Config

logger = logging.getLogger(__name__)

class VeraDataExportHandler:
    def __init__(self):
        self.broker = Config.MQTT_BROKER
        self.port = Config.MQTT_PORT
        self.username = Config.MQTT_USER
        self.password = Config.MQTT_PASSWORD
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        self.connected = False
        self.message_cache = {}
        self.cache_timeout = 5000
        self.cache_lock = threading.Lock()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"Vera export connected to {self.broker}:{self.port}")
        else:
            logger.error(f"Vera export connection error: {rc}")

    def _get_cache_key(self, message):
        return f"{message.get('room')}_{message.get('device')}_{message.get('type')}"

    def _is_duplicate(self, message):
        cache_key = self._get_cache_key(message)
        current_time = time.time() * 1000  # Convert to milliseconds
        
        with self.cache_lock:
            if cache_key in self.message_cache:
                last_time = self.message_cache[cache_key]
                if current_time - last_time < self.cache_timeout:
                    return True
            
            self.message_cache[cache_key] = current_time
            return False

    def send_event(self, message):
        try:
            if not self.connected:
                logger.warning("MQTT not connected, skipping export")
                return False

            if self._is_duplicate(message):
                logger.debug(f"Duplicate event filtered: {message}")
                return False
            # set the mqtt topic
            topic = f"vera/events/{message.get('room', 'unknown')}/{message.get('device', 'unknown')}"
            payload = json.dumps(message, ensure_ascii=False)
            
            self.client.publish(topic, payload)
            logger.debug(f"Event exported to MQTT: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False

    def connect(self):
        try:
            if not self.connected:
                self.client.connect(self.broker, self.port, 60)
                self.client.loop_start()
        except Exception as e:
            logger.error(f"Export connection error: {e}")

    def disconnect(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
        except Exception as e:
            logger.error(f"Export disconnect error: {e}")