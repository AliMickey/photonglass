import logging, requests, ipaddress, validators
from functools import wraps
from flask import request, current_app, jsonify

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


# Raised when user input is rejected, so the message is safe to return to the client
class InputError(Exception):
    pass


# Exception handler
def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InputError as e:
            # Recorded without a webhook, as a rejected target is usually just a typo
            logger.warning(f"Rejected input in {func.__name__}: {e}")
            return jsonify({'error': True, 'message': str(e)}), 400

        except Exception as e:
            logging.exception(f"Exception occurred in {func.__name__}")

            webhook = current_app.config['CONFIG'].get('webhook')

            if webhook:
                send_webhook(webhook['url'], f"Exception: `{str(e)}`")

            return jsonify({'error': True, 'message': 'An error occurred.'}), 500
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

        response = requests.post(webhook_url, json=payload, headers=headers, timeout=(3, 5))
        response.raise_for_status()
    
    except Exception as e:
        logger.error(f"Failed to send webhook: {e}")


# Get client IP address
def get_client_ip():
    if not request.headers.getlist("X-Forwarded-For"):
        return request.remote_addr
    return request.headers.getlist("X-Forwarded-For")[0]


# Whether a target is reachable on the public internet, which a hostname always may be
def is_global_target(value):
    # A prefix is only global when both of its ends are, which its own is_global allows for
    if isinstance(value, (ipaddress.IPv4Network, ipaddress.IPv6Network)):
        return value.network_address.is_global and value.broadcast_address.is_global

    if isinstance(value, str):
        return True

    return value.is_global


# Validate the target string against the format its command takes
def get_validated_target(target_string, field, allow_private=False):
    if len(target_string) > 255:
        return False, "Input exceeds max length"

    target_type = str(field.get('type') or 'text').strip().lower()

    if target_type == 'address':
        try:
            value = ipaddress.ip_address(target_string)

        except ValueError:
            return False, "Input is not a valid IP address"

    elif target_type == 'prefix':
        try:
            network = ipaddress.ip_network(target_string, strict=False)

        except ValueError:
            return False, "Input is not a valid IP address or prefix"

        # A target typed without a mask stays an address rather than becoming a host prefix
        value = network if '/' in target_string else network.network_address

    elif target_type == 'hostname':
        if not validators.domain(target_string):
            return False, "Input is not a valid hostname"

        value = target_string

    else:
        try:
            value = ipaddress.ip_address(target_string)

        except ValueError:
            if not validators.domain(target_string):
                return False, "Input is not a valid IP or domain"

            value = target_string

    if not allow_private and not is_global_target(value):
        return False, "Non-global IP address provided"

    return True, value