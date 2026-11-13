## Configuration
### Logos and favicon
If you wish to use custom assets, create the images folder under /instance and map it in docker-compose.yml. Any web image format may be used (svg, png, jpg, webp, ico), set the filenames under `header` in `site.yaml`:
  - `favicon` (default `favicon.svg`)
  - `logo_light` (default `logo-light.svg`)
  - `logo_dark` (default `logo-dark.svg`)

Each of these may instead be an `https://` image URL, which is used as-is and needs no images folder, for example `logo_light: "https://example.com/logo-light.svg"`. Anything else is treated as a filename.


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

### Config files
On first start, any of `config.yaml`, `site.yaml`, `commands.yaml` and `devices.yaml` that are missing from `/instance` are copied there from [app/examples](app/examples). Edit them and restart the container to apply.

Notes:
  - `theme` accepts `auto`, `light` or `dark`. `light` and `dark` hide the toggle.
  - `max_devices` caps how many devices a single query may run against, `0` (the default) allows every device.
  - `allow_private` lets a query target private and reserved addresses, `false` (the default) rejects them.
  - A command `format` may use the `{ip_version}` and `{target}` placeholders.
  - A command may set `field.type` to `address`, `prefix` or `hostname` to pick the target format it takes. `text` (the default) takes an IP address or a hostname.
  - A device may only run the commands listed under its `commands` key.
  - Device credentials always need a `username`, plus either a `password` or an `ssh_key`, where `ssh_key` is a filename inside `/instance/ssh-keys`. The container runs as `appuser`, so the key file must be readable by that user, for example `sudo chown $(docker exec photonglass id -u) instance/ssh-keys/id_ed25519`.
  - A device with `exec: true` runs each command over an SSH exec channel instead of an interactive shell. Use it for hosts that refuse interactive logins, such as a restricted shell set as the user's login shell or forced command that only runs the command passed to `ssh`.
