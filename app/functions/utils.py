import os, yaml, logging, requests
from functools import wraps
from flask import request

logger = logging.getLogger(__name__)


# Exception handler
def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Exception occurred in {func.__name__}")
            return "An error occurred", 500
    return wrapper


# Load YAML configuration file
@exception_handler
def load_yaml(filename, key=None):
    if not filename.endswith('.yaml'):
        filename = f"{filename}.yaml"

    config_path = os.path.join("/instance", filename)

    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        return {}

    try:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            if data is None:
                logger.warning(f"Empty configuration file: {filename}")
                return {}
            
            # Return specific key if provided
            if key:
                return data.get(key, None)
            
            return data
        
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in {filename}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading {filename}: {e}")
        return {}
    

# Send data to a webhook URL
@exception_handler
def send_webhook(webhook_url, text_data):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "text": text_data
    }

    response = requests.post(webhook_url, json=payload, headers=headers)
    response.raise_for_status()


# Get client IP address
@exception_handler
def get_client_ip():
    if not request.headers.getlist("X-Forwarded-For"):
        return request.remote_addr
    return request.headers.getlist("X-Forwarded-For")[0]