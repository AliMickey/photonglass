import logging
from copy import deepcopy
from flask import Blueprint, request, render_template, current_app

from app.functions.utils import exception_handler, send_webhook, get_client_ip, is_target_valid
from app.functions.netmiko import execute_command

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

bp = Blueprint('main', __name__)


# Route to render the main page
@bp.route('/')
@exception_handler
def index():
    site = current_app.config['SITE']
    devices = deepcopy(current_app.config['DEVICES'])
    commands = current_app.config['COMMANDS']

    for device in devices.values():
        device.pop('credentials', None)

    return render_template('index.html', site=site, devices=devices, commands=commands)


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
    
    # Validate target IP address
    if not is_target_valid(input_target):
        raise Exception(f"Invalid target: '{input_target}'")

    device = current_app.config['DEVICES'].get(input_device, {})
    command = current_app.config['COMMANDS'].get(input_command, {})

    # Verify device and command exist
    if not device or not command:
        raise Exception("Device or command not found")
    
    # Verify command is allowed for this device
    if input_command not in device.get('commands', []):
        raise Exception("Command not allowed for this device")

    # Execute the command using network_utils
    ip_version = 6 if input_ip_version == "IPv6" else 4
    result = execute_command(device, command['format'], input_target, ip_version)

    # Send a webhook notification with client IP and command output
    webhook = current_app.config['CONFIG'].get('webhook')
    if not result['error'] and webhook:
        client_ip = get_client_ip()
        send_webhook(webhook['url'], f"Client IP: `{client_ip}`\nDevice: `{input_device}`\nCommand: `{input_command} -{ip_version} {input_target}`")

    return result