import logging, os
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

paramiko_logger = logging.getLogger("paramiko")
paramiko_logger.setLevel(logging.WARNING)

# Establish connection to network device
def establish_connection(device_config):
    try:
        return ConnectHandler(**device_config)
    except Exception as e:
        logger.error(f"Failed to establish connection to {device_config['host']}: {e}")
        raise


# Execute command on network device
def execute_command(device, command_format, target, ip_version):
    device_config = {
        'device_type': device['type'],
        'host': device['host'],
        'port': device['port'],
        'username': device['username'],
        'timeout': 10,
        'session_timeout': 60,
        'conn_timeout': 10,
        'auth_timeout': 10,
    }

    # Use SSH key if provided
    if "ssh_key" in device:
        key_path = os.path.join("/instance/ssh-keys", device['ssh_key'])

        if not os.path.exists(key_path):
            logger.error(f"SSH file not found: {key_path} for {device['host']}")
            return {'error': True, 'message': 'Authentication failed'}
        
        device_config['use_keys'] = True
        device_config['key_file'] =  os.path.join("/instance/ssh-keys", device['ssh_key'])

    else:
        device_config['password'] = device['password']

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
