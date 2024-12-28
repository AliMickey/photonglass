import logging, requests
from functools import wraps
from flask import request

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