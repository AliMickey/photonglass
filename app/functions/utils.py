import logging, requests, ipaddress, validators
from functools import wraps
from flask import request, current_app

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


# Exception handler
def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Exception occurred in {func.__name__}")
            send_webhook(current_app.config['CONFIG'].get('webhook')['url'], f"Exception: `{str(e)}`")
            return None
    return wrapper
    

# Send data to a webhook URL
def send_webhook(webhook_url, text_data):
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            "text": text_data
        }

        response = requests.post(webhook_url, json=payload, headers=headers)
        response.raise_for_status()
    
    except Exception as e:
        logger.error(f"Failed to send webhook: {e}")


# Get client IP address
@exception_handler
def get_client_ip():
    if not request.headers.getlist("X-Forwarded-For"):
        return request.remote_addr
    return request.headers.getlist("X-Forwarded-For")[0]


# Validate if the target string is a valid IP address or domain
@exception_handler
def get_validated_target(target_string):
    if len(target_string) > 255:
        raise ValueError(f"Validation failed: Input exceeds max length.")
    
    try:
        ip_obj = ipaddress.ip_address(target_string)

        if not ip_obj.is_global:
            raise ValueError(f"Validation failed: Non-global IP address provided.")

        return ip_obj

    except ValueError:
        if not validators.domain(target_string):
            raise ValueError(f"Validation failed: Input is not a valid IP or domain.")

        return target_string