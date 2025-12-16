import paho.mqtt.client as mqtt
import json
import logging
import threading
from http_client import HTTPClient
from config import Config
from vera_data_handler import VeraDataProcessor
from ip_client import ip_client
from vera_http_event_handler import VeraHTTPHandler

class MQTTHandler:
    def __init__(self):
        self.broker = Config.MQTT_BROKER
        self.port = Config.MQTT_PORT
        self.username = Config.MQTT_USER
        self.password = Config.MQTT_PASSWORD
        self.http_client = HTTPClient()
        self.vera_processor = VeraDataProcessor()
        self.vera_upnp = VeraHTTPHandler()
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        self.logger = logging.getLogger(__name__)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info(f"Connected to {self.broker}:{self.port}")
            client.subscribe("client/con_ip")
            client.subscribe("read/data")
            # Start Vera handler in the background 
            self.vera_upnp.start()
        else:
            self.logger.error(f"Connection error: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode('utf-8')
            
            if msg.topic == "client/con_ip":
                self._handle_ip_message(payload_str)
            elif msg.topic == "read/data" and payload_str.strip().lower() == "vera":
                self._handle_vera_data_request()
                
        except Exception as e:
            self.logger.error(f"Message error: {e}")

    def _handle_ip_message(self, payload_str: str):
        try:
            ip_updated = ip_client.update_ip_from_message("client/con_ip", payload_str)
            if ip_updated:
                self.logger.info("IP updated")
        except Exception as e:
            self.logger.error(f"IP update error: {e}")

    def _handle_vera_data_request(self):
        try:
            self.logger.info("Manual Vera data request")
            vera_data = self.vera_processor.get_vera_device_list()
            if vera_data:
                success = self.http_client.send_data(vera_data, Config.HTTP_STATE_PORT)
                if success:
                    self.logger.info("Manual data sent")
                else:
                    self.logger.error("Failed to send manual data")
            else:
                self.logger.error("No Vera data received")
                
        except Exception as e:
            self.logger.error(f"Manual request error: {e}")

    def start(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_forever()
        except Exception as e:
            self.logger.error(f"MQTT error: {e}")

    def stop(self):
        self.vera_upnp.stop()
        self.client.disconnect()