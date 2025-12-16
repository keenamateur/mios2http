import os
import re
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MQTT beállítások
    MQTT_BROKER = os.getenv('MQTT_BROKER', '')
    MQTT_USER = os.getenv('MQTT_USER', 'gtladmin')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')

    # Portok kezelése (üres string esetén default érték)
    mqtt_port_str = os.getenv('MQTT_PORT', '')
    MQTT_PORT = (
        int(mqtt_port_str) 
        if mqtt_port_str.isdigit()
        else 52888
    )
    
    # HTTP beállítások
    HTTP_CLIENT_IP = os.getenv('HTTP_CLIENT_IP', '192.168.2.100')

    http_device_port_str = os.getenv('HTTP_DEVICE_PORT', '')
    HTTP_DEVICE_PORT = (
        int(http_device_port_str)
        if http_device_port_str.isdigit()
        else 1910
    )
    
    http_state_port_str = os.getenv('HTTP_STATE_PORT', '')
    HTTP_STATE_PORT = (
        int(http_state_port_str)
        if http_state_port_str.isdigit()
        else 1904
    )
    
    # Vera beállítások
    VERA_IP = os.getenv('VERA_IP', '192.168.4.10')

    vera_port_str = os.getenv('VERA_PORT', '')
    VERA_PORT = int(vera_port_str) if vera_port_str.isdigit() else 3480

    VERA_EVENT_FILTER = os.getenv('VERA_EVENT_FILTER', '')
    
    ALLOWED_ROOMS = [
        "Nappali", "Sátor", "Konyha", "Fürdő", "Háló", "Terasz",
        "Biztonság", "Műhely", "Garázs", "Áram", "Szerver", "Szenzor"
    ]
    
    @staticmethod
    def validate_ip(ip):
        if not ip:
            return False
        return bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip))
    
    @classmethod
    def print_config(cls):
        """Kiírja a konfigurációt (jelszavak nélkül)"""
        print("=== Konfiguráció ===")
        print(f"MQTT Broker: {cls.MQTT_BROKER}")
        print(f"MQTT Port: {cls.MQTT_PORT}")
        print(f"MQTT User: {cls.MQTT_USER}")
        print(f"MQTT Password: {'*' * len(cls.MQTT_PASSWORD) if cls.MQTT_PASSWORD else 'None'}")
        print(f"HTTP Client IP: {cls.HTTP_CLIENT_IP}")
        print(f"HTTP Device Port: {cls.HTTP_DEVICE_PORT}")
        print(f"HTTP State Port: {cls.HTTP_STATE_PORT}")
        print(f"Vera IP: {cls.VERA_IP}")
        print(f"Vera Port: {cls.VERA_PORT}")
        print(f"Vera Event Filter: {cls.VERA_EVENT_FILTER}")