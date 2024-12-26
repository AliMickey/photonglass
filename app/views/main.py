from flask import (
    Blueprint, request, render_template
)
import logging

from app.functions.utils import load_yaml, execute_command, exception_handler

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

@bp.route('/')
@exception_handler
def index():
    config = load_yaml('config')
    devices = load_yaml('devices')
    commands = load_yaml('commands')

    # Remove sensitive data before passing to Jinja as additional security measure
    for device in devices:
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
    device = data.get('device')
    command = data.get('command')
    target = data.get('target')
    ip_version = data.get('ipVersion')

    if not all([device, command, target, ip_version]):
        raise Exception("Missing required parameters")

    # Load configurations
    devices = load_yaml('devices')
    commands = load_yaml('commands')

    # Find device and command configurations
    device = next((d for d in devices if d['id'] == device), None)
    command = next((c for c in commands if c['id'] == command), None)

    if not device or not command:
        raise Exception("Device or command not found")

    # Verify command is allowed for this device
    if command['id'] not in device.get('commands', []):
        raise Exception("Command not allowed for this device")

    ip_version = 6 if ip_version == "IPv6" else 4

    # Execute the command using network_utils
    result = execute_command(device, command['format'], target, ip_version)

    return result
