import logging, os, time
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

paramiko_logger = logging.getLogger("paramiko")
paramiko_logger.setLevel(logging.WARNING)

COMMAND_TIMEOUT = 30
READ_INTERVAL = 0.1

# Establish connection to network device
def establish_connection(device_config):
    try:
        return ConnectHandler(**device_config)
    except Exception as e:
        logger.error(f"Failed to establish connection to {device_config['host']}: {e}")
        raise


# Read the channel in chunks and yield output as the device produces it
def stream_output(connection, command, timeout=COMMAND_TIMEOUT):
    prompt = connection.find_prompt()
    connection.write_channel(command + connection.RETURN)

    deadline = time.monotonic() + timeout
    buffer = ""
    echo_stripped = False
    started = False

    while time.monotonic() < deadline:
        chunk = connection.read_channel()

        if not chunk:
            time.sleep(READ_INTERVAL)
            continue

        buffer += chunk

        # Drop the echo of the command itself
        if not echo_stripped:
            if "\n" not in buffer:
                continue

            echoed, remainder = buffer.split("\n", 1)
            if command in echoed:
                buffer = remainder
            echo_stripped = True

        if not started:
            buffer = buffer.lstrip()

        # The prompt reappearing marks the end of the output
        if prompt in buffer:
            buffer = buffer.split(prompt, 1)[0]
            break

        # Emit whole lines only, holding any partial line back for the next read
        if "\n" in buffer:
            emitted, buffer = buffer.rsplit("\n", 1)
            started = True
            yield emitted + "\n"
    else:
        logger.error(f"Timed out after {timeout}s waiting for the prompt on {connection.host}")

    buffer = buffer.rstrip()
    if buffer:
        yield buffer


# Execute command on network device
def execute_command(device, command_format, target, ip_version):
    device_credentials = device['credentials']

    device_config = {
        'device_type': device['type'],
        'host': device_credentials['host'],
        'port': device_credentials['port'],
        'username': device_credentials['username'],
        'timeout': 10,
        'session_timeout': 60,
        'conn_timeout': 10,
        'auth_timeout': 10,
    }

    # Use SSH key if provided
    if "ssh_key" in device_credentials:
        key_path = os.path.join("/instance/ssh-keys", device_credentials['ssh_key'])

        if not os.path.exists(key_path):
            logger.error(f"SSH file not found: {key_path} for {device_credentials['host']}")
            yield {'error': True}
            return
        
        device_config['use_keys'] = True
        device_config['key_file'] = key_path

    else:
        device_config['password'] = device_credentials['password']


    try:
        with establish_connection(device_config) as connection:
            # Format the command
            command = str(command_format.format(ip_version=ip_version, target=target).strip())

            # Execute the command
            produced_output = False
            for chunk in stream_output(connection, command):
                produced_output = True
                yield {'error': False, 'message': chunk}

            if not produced_output:
                logger.error(f"No response from {device_config['host']}")
                yield {'error': True}
                return

            # Sent before the connection is torn down, which netmiko does slowly
            yield {'done': True}

    except NetmikoTimeoutException as e:
        logger.error(f"Timeout error on {device_config['host']}: {e}")
        yield {'error': True}
    
    except NetmikoAuthenticationException as e:
        logger.error(f"Authentication failed for {device_config['host']}: {e}")
        yield {'error': True}
    
    except Exception as e:
        logger.error(f"An unexpected error occurred on {device_config['host']}: {e}")
        yield {'error': True}
