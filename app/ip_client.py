import json
import logging
import os
import re
from typing import Any
from config import Config

logger = logging.getLogger(__name__)

class IPClient:
    def __init__(self):
        self.current_ip = os.getenv('HTTP_CLIENT_IP', '192.168.1.100')
        logger.info(f"IPClient started with IP: {self.current_ip}")
    
    def update_ip_from_message(self, topic: str, payload: Any) -> bool:
        if topic != "client/con_ip":
            return False
        
        try:
            new_ip = self._extract_ip(payload)
            if not new_ip or not self._validate_ip(new_ip):
                return False
            
            if new_ip != self.current_ip:
                logger.info(f"IP changed: {self.current_ip} -> {new_ip}")
                self.current_ip = new_ip
                self._update_config()
                return True
            
            return False
                
        except Exception as e:
            logger.error(f"IP update error: {e}")
            return False
    
    def _extract_ip(self, payload: Any) -> str:
        if isinstance(payload, dict):
            return payload.get('ip', '')
        elif isinstance(payload, str):
            try:
                data = json.loads(payload)
                return data.get('ip', '') if isinstance(data, dict) else payload.strip()
            except json.JSONDecodeError:
                return payload.strip()
        return ''
    
    def _validate_ip(self, ip: str) -> bool:
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
            return False
        return all(0 <= int(part) <= 255 for part in ip.split('.'))
    
    def _update_config(self):
        try:
            env_file = '.env'
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    if line.startswith('HTTP_CLIENT_IP='):
                        lines[i] = f'HTTP_CLIENT_IP={self.current_ip}\n'
                        break
                else:
                    lines.append(f'HTTP_CLIENT_IP={self.current_ip}\n')
                
                with open(env_file, 'w') as f:
                    f.writelines(lines)
            
            os.environ['HTTP_CLIENT_IP'] = self.current_ip
            logger.info(f"Config updated: {self.current_ip}")
            
        except Exception as e:
            logger.error(f"Config update error: {e}")
    
    def get_current_ip(self) -> str:
        return self.current_ip

ip_client = IPClient()