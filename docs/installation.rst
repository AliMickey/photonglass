Installation
===========

This guide covers Docker deployment options for photonglass.

Requirements
-----------
* Docker and Docker Compose
* Network access to target devices

Deployment
---------------

1. Clone the repository::

    git clone <repository-url>
    cd looking-glass

2. Configure the application::

    cp instance/config.yaml.example instance/config.yaml
    cp instance/commands.yaml.example instance/commands.yaml
    cp instance/devices.yaml.example instance/devices.yaml

3. Build and start the containers::

    docker compose up -d

   This will:
   - Build the application image
   - Start the web application container
   - Initialize the TailwindCSS build process

4. Access the application at ``http://localhost:5000``

Configuration Files
-----------------

The application uses three main configuration files:

1. ``instance/config.yaml``
   - Core application settings
   - UI customization
   - Logging configuration

2. ``instance/commands.yaml``
   - Network diagnostic commands
   - Command parameters and validation rules
   - Output formatting options

3. ``instance/devices.yaml``
   - Network device definitions
   - Authentication credentials
   - Access control rules

See the :doc:`configuration` section for detailed configuration options.

Security Considerations
---------------------

1. Always change default credentials
2. Use strong passwords for database and application access
3. Configure appropriate network access controls
4. Regularly update dependencies
5. Monitor application logs for security events

Next Steps
---------
After installation, refer to:

- :doc:`configuration` for detailed setup options
- :doc:`usage` for operation instructions
- :doc:`api` for API documentation