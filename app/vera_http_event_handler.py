# vera_http_event_handler.py

import json
import requests
import re
import time
import logging
import threading
from config import Config
from http_client import HTTPClient
from ip_client import ip_client
from vera_data_export_handler import VeraDataExportHandler

logger = logging.getLogger(__name__)

class VeraHTTPHandler:
    def __init__(self):
        self.vera_ip = Config.VERA_IP
        self.vera_port = Config.VERA_PORT
        self.http_client = HTTPClient()
        self.export_handler = VeraDataExportHandler()
        self.filter_patterns = self._parse_filter_config()
        self.devices = {}
        self.running = False
        self.last_states = {}
        self.event_cache = {}
        self.session = requests.Session()
        self.cache_lock = threading.Lock()
        self.cache_timeout = 3000

    def _parse_filter_config(self):
        try:
            filter_config = getattr(Config, 'VERA_EVENT_FILTER', '')
            logger.info(f"Filter config: '{filter_config}'")
            
            if not filter_config:
                return []
            
            patterns = []
            for item in filter_config.split('#'):
                if not item:
                    continue
                    
                if ':' in item:
                    room_part, device_pattern = item.split(':', 1)
                    patterns.append({
                        'room': room_part.strip(),
                        'device_pattern': device_pattern.strip().replace('*', '.*')
                    })
                else:
                    patterns.append({
                        'room': item.strip(),
                        'device_pattern': None
                    })
            
            logger.info(f"Parsed {len(patterns)} filter patterns")
            return patterns
        except Exception as e:
            logger.error(f"Error parsing filter config: {e}")
            return []

    def _get_cache_key(self, device_id, variable, value):
        return f"{device_id}_{variable}_{value}"

    def _is_duplicate_event(self, device_id, variable, value):
        cache_key = self._get_cache_key(device_id, variable, value)
        current_time = time.time() * 1000
        
        with self.cache_lock:
            if cache_key in self.event_cache:
                last_time = self.event_cache[cache_key]
                if current_time - last_time < self.cache_timeout:
                    return True
            
            self.event_cache[cache_key] = current_time
            return False

    def fetch_devices(self):
        try:
            url = f"http://{self.vera_ip}:{self.vera_port}/data_request?id=lu_sdata&output_format=json"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self.process_device_data(data)
            else:
                logger.error(f"HTTP error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error fetching devices: {e}")
            return False

    def process_device_data(self, data):
        try:
            self.devices = {}
            for room in data.get('rooms', []):
                self.devices[room['id']] = {'name': room['name'], 'devices': []}

            device_count = 0
            for device in data.get('devices', []):
                room_id = device['room']
                if room_id in self.devices:
                    self.devices[room_id]['devices'].append({
                        'id': device['id'],
                        'name': device['name'],
                        'category': device.get('category')
                    })
                    device_count += 1
            
            logger.info(f"Processed {len(self.devices)} rooms with {device_count} devices")
            return True
            
        except Exception as e:
            logger.error(f"Device data processing error: {e}")
            return False

    def _matches_filter(self, room_name, device_name):
        if not self.filter_patterns:
            return False
            
        for pattern in self.filter_patterns:
            if pattern['room'].lower() != room_name.lower():
                continue
                
            if pattern['device_pattern'] is None:
                return True
                
            try:
                regex_pattern = f"^{pattern['device_pattern']}$"
                if re.match(regex_pattern, device_name, re.IGNORECASE):
                    return True
            except re.error as e:
                logger.error(f"Regex error: {e}")
                
        return False

    def poll_status_changes(self):
        try:
            url = f"http://{self.vera_ip}:{self.vera_port}/data_request?id=status&output_format=json"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.process_status_data(data)
                return True
            else:
                logger.error(f"Status poll error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Poll error: {e}")
            return False

    def process_status_data(self, status_data):
        try:
            if 'devices' not in status_data:
                return
                
            processed_count = 0
            for device in status_data['devices']:
                if 'states' in device:
                    for state in device['states']:
                        if 'variable' in state and 'value' in state:
                            device_id = device['id']
                            variable = state['variable']
                            value = state['value']
                            
                            if variable in ['Status', 'LoadLevelStatus', 'Tripped']:
                                if self._is_duplicate_event(device_id, variable, value):
                                    logger.debug(f"Duplicate event filtered: {device_id} {variable} {value}")
                                    continue
                                    
                                message = self.create_status_message(device_id, variable, value)
                                if message:
                                    # Send via HTTP
                                    self.http_client.send_data(message, Config.HTTP_DEVICE_PORT)
                                    # Send via MQTT export
                                    self.export_handler.send_event(message)
                                    processed_count += 1
            
            if processed_count > 0:
                logger.info(f"Sent {processed_count} status changes")
                                    
        except Exception as e:
            logger.error(f"Status data processing error: {e}")

    def create_status_message(self, device_id, variable, value):
        try:
            device_info = None
            room_name = ""
            
            for room_id, room_data in self.devices.items():
                for device in room_data['devices']:
                    if device['id'] == device_id:
                        device_info = device
                        room_name = room_data['name']
                        break
                if device_info:
                    break
            
            if not device_info:
                logger.debug(f"Device {device_id} not found in cache")
                return None
                
            if not self._matches_filter(room_name, device_info['name']):
                return None

            key = f"{device_id}_{variable}"
            if self.last_states.get(key) == value:
                return None

            self.last_states[key] = value

            converted_value = self._convert_value(value, variable)
            if converted_value is None:
                return None

            message = {
                'room': room_name,
                'device': device_info['name'],
                'type': variable,
                'value': converted_value
            }
            
            logger.info(f"Status change: {message}")
            return message
            
        except Exception as e:
            logger.error(f"Message creation error: {e}")
            return None

    def _convert_value(self, value, var_type):
        try:
            if isinstance(value, bool):
                return 1 if value else 0
            
            if isinstance(value, str):
                value = value.strip().lower()
                if value in ['true', 'on', '1']:
                    return 1
                elif value in ['false', 'off', '0']:
                    return 0
            
            if var_type == "LoadLevelStatus":
                return float(value) if value != "" else 0
            elif var_type == "Status":
                return 1 if float(value) > 0 else 0
            elif var_type == "Tripped":
                return 1 if str(value).lower() in ['true', 'on', '1'] else 0
            
            return float(value) if value != "" else 0
            
        except (ValueError, TypeError):
            return None

    def event_loop(self):
        success = self.fetch_devices()
        if not success:
            logger.error("Failed to fetch device data")
            return

        # Connect MQTT export handler
        self.export_handler.connect()

        logger.info("Starting status polling")
        while self.running:
            try:
                self.poll_status_changes()
                time.sleep(2)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)

    def start(self):
        if not self.running:
            self.running = True
            import threading
            self.thread = threading.Thread(target=self.event_loop, daemon=True)
            self.thread.start()
            logger.info("Vera handler started")

    def stop(self):
        if self.running:
            self.running = False
            self.export_handler.disconnect()
            logger.info("Vera handler stopped")