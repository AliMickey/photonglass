Configuration
============

This section details all configuration options available in the Looking Glass application.

Core Configuration (config.yaml)
------------------------------

The ``instance/config.yaml`` file contains core application settings and UI customization options.

Site Settings
~~~~~~~~~~~~

.. code-block:: yaml

    site:
      title: "photonglass"  # Application title displayed in browser
      favicon: "/static/images/default-favicon.svg"  # Site favicon path

Logo Configuration
~~~~~~~~~~~~~~~~

.. code-block:: yaml

    logo:
      dark: "/static/images/default-logo-dark.svg"   # Logo for dark mode
      light: "/static/images/default-logo-light.svg" # Logo for light mode

Footer Settings
~~~~~~~~~~~~~

.. code-block:: yaml

    footer:
      text: "photonglass"  # Footer text
      external_links:      # External links in footer
        peeringdb: "https://www.peeringdb.com"
        github: "https://github.com/AliMickey/photonglass" # For credit, remove if you want :)

Network Commands (commands.yaml)
-----------------------------

The ``instance/commands.yaml`` file defines available network diagnostic commands and their parameters.

Command Definition Format
~~~~~~~~~~~~~~~~~~~~~~~

Each command is defined with the following structure:

.. code-block:: yaml

    - id: "command_id"              # Unique identifier for the command
      display_name: "Command Name"  # Display name in the UI
      format: "command {target}"    # Command format with placeholders
      description: "Description"    # Command description
      field:                       # Input field configuration
        type: "text"              # Input field type
        placeholder: "Enter..."   # Placeholder text

Available Commands
~~~~~~~~~~~~~~~~

Ping Command
^^^^^^^^^^^

.. code-block:: yaml

    - id: "ping"
      display_name: "Ping"
      format: "ping -c 4 {target}"
      description: "Test network connectivity"
      field:
        type: "text"
        placeholder: "Enter IP address or hostname"

Traceroute Command
^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    - id: "traceroute"
      display_name: "Traceroute"
      format: "traceroute {target}"
      description: "Trace network path to destination"
      field:
        type: "text"
        placeholder: "Enter IP address or hostname"

MTR Command
^^^^^^^^^^

.. code-block:: yaml

    - id: "mtr"
      display_name: "MTR"
      format: "mtr -r {target}"
      description: "My Traceroute - Network diagnostic tool"
      field:
        type: "text"
        placeholder: "Enter IP address or hostname"

Network Devices (devices.yaml)
---------------------------

The ``instance/devices.yaml`` file contains network device configurations and access control settings.

Device Configuration Format
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    - id: "device_id"                  # Unique device identifier
      name: "Device Name"             # Display name
      type: "router/switch"          # Device type
      location: "Location Name"      # Physical location
      host: "192.168.1.1"             # Management IP address
      port: 22                        # SSH port
      credentials:                   # Access credentials
        username: "admin"
        key_file: "/path/to/key"    # SSH key file path
      commands:                     # List of allowed commands
          - "ping"
          - "traceroute"


Security Recommendations
---------------------

1. Credentials and Secrets
   - Never commit sensitive information to version control
   - Use environment variables for secrets
   - Regularly rotate credentials

2. Network Access
   - Implement strict ACLs for command targets
   - Use allowlists for permitted networks
   - Rate limit command execution

3. Authentication
   - Enable HTTPS in production
   - Implement user authentication if needed
   - Use strong password policies

4. Monitoring
   - Enable logging for all command executions
   - Monitor system resources
   - Set up alerts for suspicious activities

For more information about security best practices, refer to the :doc:`security` section.

Custom Commands
~~~~~~~~~~~~~

To add custom network commands:

1. Add command definition to ``commands.yaml``
2. Implement command validation if needed
3. Update the UI help documentation
4. Test the command execution

Refer to the :doc:`development` section for more details about extending the application.
