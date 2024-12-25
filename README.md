# photonglass
A modern, distributed looking glass application that provides network insight for network operators.


## Features
-**Multi-Device Support**: Connect to multiple devices from one single interface.
-**Easy Deployment**: Extremely easy to deploy and scale with multiple devices.


## Setup (Docker)
1. Clone repository
    - `git clone https://github.com/AliMickey/photonglass.git`
2. Create an instance folder to store your config and logos
    - `cd photonglass`
    - `mkdir instance`
    - `mkdir instance/images`
3. Create config files and upload logos (follow config template below)
4. Edit `docker-compose.yml` if required (images path is commented out by default)
4. Build and deploy the container
    - `docker compose up -d --build`
5. View the app at `http://IP_ADDRESS:5000`, recommend using a reverse proxy (traefik) for production use. 


## Configuration
### instance/config.yaml
```
header:
  title: "photonglass"
  logo_href: "#"

footer:
  text: "photonglass"
  peeringdb_href: "https://www.peeringdb.com"
  github_href: "https://github.com/alimickey"

```

### instance/commands.yaml
```
- id: "ping"
  display_name: "Ping"
  format: "ping -{ip_version} -c 4 {target}"
  description: "Test network connectivity"
  field:
    type: "text"
    placeholder: "Enter IP address or hostname"

- id: "traceroute"
  display_name: "Traceroute"
  format: "traceroute -{ip_version} {target}"
  description: "Trace network path to destination"
  field:
    type: "text"
    placeholder: "Enter IP address or hostname"

- id: "mtr"
  display_name: "MTR"
  format: "mtr -{ip_version} -r {target}"
  description: "Trace network path with stats"
  field:
    type: "text"
    placeholder: "Enter IP address or hostname"
```

### instance/devices.yaml
```
- id: "unique-sydney"
  display_name: "Sydney"
  subtext: "Equinix SY3"
  country_code: "AU"
  type: "linux"
  host: "IP_ADDRESS"
  port: PORT
  username: "USERNAME"
  password: "PASSWORD"
  commands:
    - ping
    - traceroute
    - mtr
```


## Attribution
This project was inspired by hyperglass after having difficulty deploying it. This project is not meant as a 1:1 replacement with hyperglass and as such is kept simple by design. At time of release only linux servers were tested as a target device, the same device library as hyperglass is used (netmiko) so compatibility with more devices should not be an issue, just be aware it is untested.