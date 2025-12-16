
import requests
import logging
import json
from ip_client import ip_client
from config import Config

class HTTPClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def send_data(self, data, port):
        try:
            current_ip = ip_client.get_current_ip()
            url = f"http://{current_ip}:{port}"
            
            self.logger.debug(f"Sending to {url}")
            
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                url, 
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers=headers, 
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Data sent to {url}")
                return True
            else:
                self.logger.error(f"Send error: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"HTTP send error: {e}")
            return False