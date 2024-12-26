import logging

from flask import Blueprint, request, render_template

from app.functions.utils import exception_handler, load_yaml, send_webhook, get_client_ip, execute_command

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)


# Route to render the main page
@bp.route('/')
@exception_handler
def index():
    config = load_yaml('config')
    devices = load_yaml('devices')
    commands = load_yaml('commands')

    # Remove sensitive data before passing to Jinja as additional security measure
    for device_key, device in devices.items():
        device.pop('username', None)
        device.pop('password', None)
        device.pop('host', None)
        device.pop('port', None)

    return render_template('index.html', config=config, devices=devices, commands=commands)


# Route to handle command execution requests
@bp.route('/execute', methods=['POST'])
@exception_handler
def execute():
    data = request.get_json()
    input_device = data.get('device')
    input_command = data.get('command')
    input_target = data.get('target').strip()
    input_ip_version = data.get('ipVersion')

    if not all([input_device, input_command, input_target, input_ip_version]):
        raise Exception("Missing required parameters")

    # Load configurations
    device = load_yaml('devices', key=input_device)
    command = load_yaml('commands', key=input_command)
    webhook = load_yaml('config', key='webhook')

    if not device or not command:
        raise Exception("Device or command not found")

    # Verify command is allowed for this device
    if input_command not in device.get('commands', []):
        raise Exception("Command not allowed for this device")

    ip_version = 6 if input_ip_version == "IPv6" else 4

    # Execute the command using network_utils
    result = execute_command(device, command['format'], input_target, ip_version)

    # Send a webhook notification with client IP and command output
    if not result['error'] and webhook:
        client_ip = get_client_ip()
        send_webhook(webhook['url'], f"Client IP: `{client_ip}`\nDevice: `{input_device}`\nCommand: `{input_command} -{ip_version} {input_target}`")

    return result
