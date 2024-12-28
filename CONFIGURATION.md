## Configuration
### Logos and favicon
If you wish to use custom assets, create the images folder under /instance, map it in docker-compose.yml and use the following filenames:
  - favicon.svg
  - logo-dark.svg
  - logo-light.svg


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

### instance/site.yaml
```
header:
  title: "photonglass"
  logo_href: "#"

footer:
  text: "photonglass"
  peeringdb_href: "https://www.peeringdb.com/net/xxx"
  github_href: "https://github.com/alimickey/photonglass"
```

### instance/config.yaml
```
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
  commands:
    - ping
    - traceroute
    - mtr
  credentials:
    host: "IP_ADDRESS"
    port: PORT
    username: "USERNAME"
    password: "PASSWORD"
    ssh_key: "id_rsa" # Optional
```
