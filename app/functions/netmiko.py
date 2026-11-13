import codecs, logging, os, socket, time
import paramiko
from netmiko import ConnectHandler, NetmikoTimeoutException

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


# Establish a plain SSH connection for devices that run commands over an exec channel
def establish_exec_connection(device_config):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=device_config['host'],
            port=device_config['port'],
            username=device_config['username'],
            password=device_config.get('password'),
            key_filename=device_config.get('key_file'),
            look_for_keys=False,
            allow_agent=False,
            timeout=device_config['conn_timeout'],
            auth_timeout=device_config['auth_timeout'],
            banner_timeout=device_config['conn_timeout'],
        )
        return client
    except Exception as e:
        client.close()
        logger.error(f"Failed to establish connection to {device_config['host']}: {e}")
        raise


# Run the command over an exec channel and yield output as the host produces it, for hosts
# whose shell refuses interactive sessions, such as a forced command reading SSH_ORIGINAL_COMMAND
def stream_exec_output(client, command, timeout=COMMAND_TIMEOUT):
    channel = client.get_transport().open_session()
    channel.set_combine_stderr(True)
    channel.exec_command(command)
    channel.settimeout(READ_INTERVAL)

    decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
    deadline = time.monotonic() + timeout
    buffer = ""

    while time.monotonic() < deadline:
        try:
            data = channel.recv(4096)
        except socket.timeout:
            continue

        # An empty read means the command finished and the host closed the channel
        if not data:
            break

        buffer += decoder.decode(data)

        # Emit whole lines only, holding any partial line back for the next read
        if "\n" in buffer:
            emitted, buffer = buffer.rsplit("\n", 1)
            yield emitted + "\n"
    else:
        logger.error(f"Timed out after {timeout}s waiting for the command to finish on {client.get_transport().getpeername()[0]}")

    channel.close()

    buffer = (buffer + decoder.decode(b"", final=True)).rstrip()
    if buffer:
        yield buffer


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

        # Drop the echo of the command itself, which blank lines can precede
        if not echo_stripped:
            stripped = buffer.lstrip("\r\n")

            if "\n" not in stripped:
                continue

            echoed, remainder = stripped.split("\n", 1)
            buffer = remainder if command in echoed or echoed.startswith(prompt) else stripped
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

        # Paramiko reports an unreadable key as a TCP connection failure, so catch it here
        if not os.access(key_path, os.R_OK):
            logger.error(f"SSH key not readable by the app user: {key_path} for {device_credentials['host']}, check its owner and permissions")
            yield {'error': True}
            return

        device_config['use_keys'] = True
        device_config['key_file'] = key_path

    else:
        device_config['password'] = device_credentials['password']


    try:
        # Format the command
        command = str(command_format.format(ip_version=ip_version, target=target).strip())

        if device.get('exec', False):
            connection, stream = establish_exec_connection(device_config), stream_exec_output
        else:
            connection, stream = establish_connection(device_config), stream_output

        with connection:
            # Execute the command
            produced_output = False
            for chunk in stream(connection, command):
                produced_output = True
                yield {'error': False, 'message': chunk}

            if not produced_output:
                logger.error(f"No response from {device_config['host']}")
                yield {'error': True}
                return

            # Sent before the connection is torn down, which netmiko does slowly
            yield {'done': True}

    except (NetmikoTimeoutException, socket.timeout) as e:
        logger.error(f"Timeout error on {device_config['host']}: {e}")
        yield {'error': True}

    # Covers netmiko's subclass of it too
    except paramiko.AuthenticationException as e:
        logger.error(f"Authentication failed for {device_config['host']}: {e}")
        yield {'error': True}
    
    except Exception as e:
        logger.error(f"An unexpected error occurred on {device_config['host']}: {e}")
        yield {'error': True}
