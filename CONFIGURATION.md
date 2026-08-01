## Configuration
### Logos and favicon
If you wish to use custom assets, create the images folder under /instance and map it in docker-compose.yml. Any web image format may be used (svg, png, jpg, webp, ico), set the filenames under `header` in `site.yaml`:
  - `favicon` (default `favicon.svg`)
  - `logo_light` (default `logo-light.svg`)
  - `logo_dark` (default `logo-dark.svg`)


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
  - A command `format` may use the `{ip_version}` and `{target}` placeholders.
  - A device may only run the commands listed under its `commands` key.
  - Device credentials take either a `password` or an `ssh_key`, where `ssh_key` is a filename inside `/instance/ssh-keys`.
