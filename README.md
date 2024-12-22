# Looking Glass Network Management

A modern web-based looking glass application that provides infrastructure monitoring and administration capabilities for network professionals. Built with Flask and Vue.js, this platform delivers real-time network analysis through an intuitive browser-based interface.

## Features

- 🌐 **Multi-Location Support**: Monitor network performance across different geographical locations
- 🔍 **Network Diagnostics**: Execute common network commands (ping, traceroute, MTR)
- 🎨 **Modern UI**: Clean, responsive interface with dark/light mode support
- 🔒 **Secure Command Execution**: Built-in input validation and command sanitization
- ⚡ **Real-Time Updates**: WebSocket-based live data streaming
- 📱 **Responsive Design**: Optimized for both desktop and mobile devices
- 🎯 **BGP Community Lookup**: Advanced BGP routing information
- 🔄 **Docker Support**: Easy deployment with containerization

## Quick Start

See our [installation guide](https://looking-glass.readthedocs.io/en/latest/installation.html) for detailed setup instructions.

## Documentation

Full documentation is available at [looking-glass.readthedocs.io](https://looking-glass.readthedocs.io/).

Key documentation sections:
- [Installation Guide](https://looking-glass.readthedocs.io/en/latest/installation.html)
- [Configuration Options](https://looking-glass.readthedocs.io/en/latest/configuration.html)
- [Usage Guide](https://looking-glass.readthedocs.io/en/latest/usage.html)
- [API Documentation](https://looking-glass.readthedocs.io/en/latest/api.html)

## Configuration

The application uses YAML configuration files for customization:

- `instance/config.yaml`: Core application settings
- `instance/commands.yaml`: Network command definitions
- `instance/devices.yaml`: Network device configurations

See the [configuration documentation](https://looking-glass.readthedocs.io/en/latest/configuration.html) for detailed options.

## Contributing

Contributions are welcome! Please read our [contributing guidelines](https://looking-glass.readthedocs.io/en/latest/contributing.html) before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.