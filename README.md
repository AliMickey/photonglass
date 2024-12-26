# photonglass
A modern, distributed looking glass application that provides network insight for network operators.

## See it live
https://photonglass.dev

[![](screenshot.png)](https://raw.githubusercontent.com/AliMickey/photonglass/7421c8a6dc1f31fef78ed5e1efb7402c89c9898c/screenshot.png)

## Features
- **Multi Device Support**: Connect to multiple devices from one single interface.
- **Easy Deployment**: Extremely easy to deploy and scale with multiple devices.
- **Webhook Logging**: Log queries to a webhook channel (optional).
- **Rate Limiting**: Reduce service abuse by rate limiting users, 100 per day and 10 per minute.

## Setup (Docker)
1. Clone repository
    - `git clone https://github.com/AliMickey/photonglass.git`
2. Create an instance folder to store your config and logos/favicon
    - `cd photonglass`
    - `mkdir instance`
    - `mkdir instance/images`
3. Create config files and upload logos/favicon (follow config template below)
4. Create `docker-compose.yml` (follow template below)
4. Build and deploy the container (inital build may take a minute)
    - `docker compose up -d --build`
5. View the app at `http://IP_ADDRESS:5000`, recommend using a reverse proxy (traefik) for production use. 


## Configuration
### docker-compose.yml
```
services:
  photonglass:
    container_name: photonglass
    restart: unless-stopped
    build: .
    ports:
      - 5000:5000
    volumes:
      - ./instance:/instance
#      - ./instance/images:/app/static/images # Commented out by default to use default logos
```

### instance/config.yaml
```
header:
  title: "photonglass"
  logo_href: "#"

footer:
  text: "photonglass"
  peeringdb_href: "https://www.peeringdb.com"
  github_href: "https://github.com/alimickey"

webhook:
  url: "https://hooks.slack.com/###"
```

### instance/commands.yaml
```
ping:
  display_name: "Ping"
  format: "ping -{ip_version} -c 4 {target}"
  description: "Test network connectivity"
  field:
    type: "text"
    placeholder: "Enter IP address or hostname"

traceroute:
  display_name: "Traceroute"
  format: "traceroute -{ip_version} {target}"
  description: "Trace network path to destination"
  field:
    type: "text"
    placeholder: "Enter IP address or hostname"

mtr:
  display_name: "MTR"
  format: "mtr -{ip_version} -r {target}"
  description: "Trace network path with stats"
  field:
    type: "text"
    placeholder: "Enter IP address or hostname"
```

### instance/devices.yaml
```
sydney1:
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
This project was inspired by [hyperglass](https://hyperglass.dev/) after having difficulty deploying it as well as being overkill for what I wanted. This project is not meant as a 1:1 replacement with hyperglass and as such is kept simple by design. At time of release only Linux servers were tested as a target device, the same device library as hyperglass is used (netmiko) so compatibility with more devices should not be an issue, just be aware it is untested.
