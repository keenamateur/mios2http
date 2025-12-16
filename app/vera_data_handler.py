import requests
import json
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class VeraDataProcessor:
    def get_vera_device_list(self):
        try:
            url = f"http://{Config.VERA_IP}:{Config.VERA_PORT}/data_request?id=lu_sdata&output_format=json"
            logger.info(f"Fetching Vera data from: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            raw_data = response.json()
            processed_data = self.process_vera_data(raw_data)
            
            if processed_data:
                logger.info(f"Processed {len(processed_data.get('devices', []))} devices")
            else:
                logger.error("Failed to process Vera data")
                
            return processed_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def process_vera_data(self, raw_data):
        try:
            if not raw_data:
                logger.error("No raw data to process")
                return None

            def get_room_name(room_id):
                for room in raw_data.get('rooms', []):
                    if room['id'] == room_id:
                        return room['name']
                return f"Unknown ({room_id})"

            def get_category_name(cat_id):
                for cat in raw_data.get('categories', []):
                    if cat['id'] == cat_id:
                        return cat['name']
                return f"Unknown ({cat_id})"

            def safe_float(value):
                if value in [None, ""]:
                    return None
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None

            rooms = []
            for room in raw_data.get('rooms', []):
                rooms.append({
                    'id': room['id'],
                    'name': room['name'],
                    'section': room.get('section')
                })

            scenes = []
            for scene in raw_data.get('scenes', []):
                scenes.append({
                    'id': scene['id'],
                    'name': scene['name'],
                    'room': get_room_name(scene.get('room', 0)),
                    'roomId': scene.get('room', 0),
                    'active': scene.get('active') == 1,
                    'state': scene.get('state'),
                    'comment': scene.get('comment', '')
                })

            devices = []
            for device in raw_data.get('devices', []):
                device_info = {
                    'id': device['id'],
                    'altId': device.get('altid'),
                    'name': device['name'],
                    'category': {
                        'id': device['category'],
                        'name': get_category_name(device['category'])
                    },
                    'subcategory': device.get('subcategory'),
                    'room': get_room_name(device.get('room', 0)),
                    'roomId': device.get('room', 0),
                    'status': device.get('status'),
                    'state': device.get('state'),
                    'configured': device.get('configured') == "1",
                    'commFailure': device.get('commFailure') == "1",
                    'parent': device.get('parent'),
                    'comment': device.get('comment', '')
                }

                temperature = safe_float(device.get('temperature'))
                humidity = safe_float(device.get('humidity'))
                
                if temperature is not None:
                    device_info['temperature'] = temperature
                if humidity is not None:
                    device_info['humidity'] = humidity
                if device['category'] == 2:  # Dimmer
                    level = safe_float(device.get('level'))
                    if level is not None:
                        device_info['level'] = level

                devices.append(device_info)

            active_scenes = sum(1 for scene in scenes if scene.get('active'))
            active_devices = sum(1 for device in devices if device.get('status') == "1")

            result = {
                'metadata': {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'veraVersion': raw_data.get('version'),
                    'model': raw_data.get('model'),
                    'serialNumber': raw_data.get('serial_number'),
                    'dataVersion': raw_data.get('dataversion')
                },
                'rooms': rooms,
                'scenes': scenes,
                'devices': devices,
                'summary': {
                    'totalRooms': len(rooms),
                    'totalScenes': len(scenes),
                    'totalDevices': len(devices),
                    'activeScenes': active_scenes,
                    'activeDevices': active_devices
                }
            }

            logger.info(f"Processed {len(devices)} devices")
            return result

        except Exception as e:
            logger.error(f"Error processing Vera data: {e}")
            return None