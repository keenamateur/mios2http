import logging
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('vera_processor.log')]
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting Vera Processor")
        
        # Import inside function to avoid circular imports
        from mqtt_handler import MQTTHandler
        mqtt_handler = MQTTHandler()
        mqtt_handler.start()
        
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()

# import logging
# from mqtt_handler import MQTTHandler

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[logging.StreamHandler(), logging.FileHandler('vera_processor.log')]
# )

# logger = logging.getLogger(__name__)

# def main():
#     try:
#         logger.info("Starting Vera Processor")
#         mqtt_handler = MQTTHandler()
#         mqtt_handler.start()
#     except KeyboardInterrupt:
#         logger.info("Stopped by user")
#     except Exception as e:
#         logger.error(f"Application error: {e}")

# if __name__ == "__main__":
#     main()