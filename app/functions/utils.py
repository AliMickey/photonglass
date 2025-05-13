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
            send_webhook(current_app.config['CONFIG'].get('webhook'), str(e))
            return "An error occurred", 500
    return wrapper
    

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


# Validate if the target string is a valid IP address or domain
@exception_handler
def is_target_valid(target_string):
    try:
        ipaddress.ip_address(target_string)
        return True
    except ValueError:
        if validators.domain(target_string):
            return True
        else:
            return False
