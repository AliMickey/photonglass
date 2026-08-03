import json, logging, queue, threading
from copy import deepcopy
from flask import Blueprint, Response, request, render_template, current_app, stream_with_context

from app.functions.utils import exception_handler, send_webhook, get_client_ip, get_validated_target
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

    theme = str(current_app.config['CONFIG'].get('theme') or 'auto').strip().lower()
    forced_theme = theme if theme in ('light', 'dark') else None

    # Cap on how many devices one query may target, where 0 is no limit
    max_devices = max(int(current_app.config['CONFIG'].get('max_devices') or 0), 0)

    return render_template('index.html', site=site, devices=devices, commands=commands,
                           forced_theme=forced_theme, max_devices=max_devices)


# Route to handle command execution requests
@bp.route('/execute', methods=['POST'])
@exception_handler
def execute():
    data = request.get_json()    
    
    input_devices = data.get('devices')
    input_command = data.get('command').strip()
    input_target = data.get('target').strip()
    input_ip_version = data.get('ipVersion').strip()

    if not isinstance(input_devices, list):
        raise Exception("Missing required parameters")

    device_keys = list(dict.fromkeys(key.strip() for key in input_devices if isinstance(key, str) and key.strip()))

    if not all([device_keys, input_command, input_target, input_ip_version]):
        raise Exception("Missing required parameters")

    max_devices = max(int(current_app.config['CONFIG'].get('max_devices') or 0), 0)

    if max_devices and len(device_keys) > max_devices:
        raise Exception(f"A query may target at most {max_devices} devices")

    target_valid, value = get_validated_target(input_target)

    if not target_valid:
        raise Exception(f"{value}: '{input_target}'")

    clean_target = str(value)

    command = current_app.config['COMMANDS'].get(input_command, {})

    if not command:
        raise Exception("Device or command not found")

    selected_devices = {}

    for device_key in device_keys:
        device = current_app.config['DEVICES'].get(device_key, {})

        # Verify device exists
        if not device:
            raise Exception("Device or command not found")

        # Verify command is allowed for this device
        if input_command not in device.get('commands', []):
            raise Exception("Command not allowed for this device")

        selected_devices[device_key] = device

    ip_version = 6 if input_ip_version == "IPv6" else 4
    webhook = current_app.config['CONFIG'].get('webhook')
    client_ip = get_client_ip()

    # Stream the output of every selected device back as newline-delimited JSON
    def generate():
        chunks = queue.Queue()
        failed = set()

        # One worker per device so slow devices never hold up the others
        def worker(device_key, device):
            try:
                for chunk in execute_command(device, command['format'], clean_target, ip_version):
                    chunks.put((device_key, chunk))
            except Exception:
                logger.exception(f"Failed to execute command on {device_key}")
                chunks.put((device_key, {'error': True, 'message': 'Unexpected error'}))
            finally:
                chunks.put((device_key, None))

        for device_key, device in selected_devices.items():
            threading.Thread(target=worker, args=(device_key, device), daemon=True).start()

        remaining = len(selected_devices)

        while remaining:
            device_key, chunk = chunks.get()

            # A worker signals it is finished by pushing None
            if chunk is None:
                remaining -= 1
                continue

            if chunk.get('error', False):
                failed.add(device_key)

            yield json.dumps({'device': device_key, **chunk}) + "\n"

        succeeded = [device_key for device_key in selected_devices if device_key not in failed]

        # Send a webhook notification with client IP and command output
        if succeeded and webhook:
            send_webhook(webhook['url'], f"Client IP: `{client_ip}`\nDevices: `{', '.join(succeeded)}`\nCommand: `{input_command} -{ip_version} {clean_target}`")

    return Response(
        stream_with_context(generate()),
        mimetype='application/x-ndjson',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )