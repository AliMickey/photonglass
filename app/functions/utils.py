import os, yaml, logging
from functools import wraps
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

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

@exception_handler
def load_yaml(filename):
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
            return data
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in {filename}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading {filename}: {e}")
        return {}
    

def establish_connection(device_config):
    try:
        return ConnectHandler(**device_config)
    except Exception as e:
        logger.error(f"Failed to establish connection to {device_config['host']}: {e}")
        raise

def execute_command(device, command_format, target, ip_version):
    device_config = {
        'device_type': device['type'],
        'host': device['host'],
        'port': device['port'],
        'username': device['username'],
        'password': device['password'],
        'timeout': 10,
        'session_timeout': 60,
        'conn_timeout': 10,
        'auth_timeout': 10,
    }

    command_timeout = 30

    try:
        with establish_connection(device_config) as connection:
            # Format the command
            command = str(command_format.format(ip_version=ip_version, target=target).strip())

            # Execute the command
            output = connection.send_command(
                command,
                read_timeout=command_timeout,
                strip_command=True,
                strip_prompt=True,
                max_loops=int(command_timeout * 10)
            )

            # Clean output
            output = output.strip() if output else ""

            if not output:
                logger.error(f"No response from {device['host']}")
                return {'error': True, 'message': 'No response from device'}

            return {'error': False, 'message': output}

    except NetmikoTimeoutException as e:
        logger.error(f"Timeout error on {device['host']}: {e}")
        return {'error': True, 'message': 'Timeout error'}
    
    except NetmikoAuthenticationException as e:
        logger.error(f"Authentication failed for {device['host']}: {e}")
        return {'error': True, 'message': 'Authentication failed'}
    
    except Exception as e:
        logger.error(f"An unexpected error occurred on {device['host']}: {e}")
        return {'error': True, 'message': 'Unexpected error'}
