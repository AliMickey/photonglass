from flask import (
    Blueprint, request, jsonify, render_template
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

    for device in devices:
        device.pop('username', None)
        device.pop('password', None)
        device.pop('host', None)
        device.pop('port', None)

    return render_template('index.html', config=config, devices=devices, commands=commands)


@bp.route('/my-ip', methods=['GET'])
@exception_handler
def get_my_ip():
    # Check headers in order of reliability
    client_ip = None

    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        client_ip = forwarded_for.split(',')[0].strip()

    if not client_ip:
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            client_ip = real_ip

    if not client_ip:
        client_ip = request.remote_addr

    return jsonify({'ip': client_ip})


@bp.route('/execute', methods=['POST'])
@exception_handler
def execute():
    data = request.get_json()
    device = data.get('device')
    command = data.get('command')
    target = data.get('target')

    if not all([device, command, target]):
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

    try:
        # Execute the command using network_utils
        result = execute_command(device, command, target)

        if not result:
            error_msg = 'No response from command execution'
            logger.error(error_msg)
            return jsonify({
                'error': True,
                'message': error_msg,
                'error_type': 'no_response'
            })

        # Check for error state
        if result.get('error', False):
            error_msg = result['raw_output']
            logger.error(f"Command execution failed: {error_msg}")
            return jsonify({
                'error': True,
                'message': error_msg,
                'error_type': result.get('error_type', 'general')
            })

        # Log successful execution
        logger.info(f"Successfully executed command {command} on {device}")

        # Return successful result
        return jsonify({
            'error': False,
            'result': result['raw_output'],
            'structured_data': result.get('structured_data')
        })

    except Exception as e:
        logger.error(f"Unexpected error during command execution: {str(e)}")
        return jsonify({
            'error': True,
            'message': f"An unexpected error occurred: {str(e)}",
            'error_type': 'general'
        })
