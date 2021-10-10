# DTMF Butler

Dockerized Python serial modem attendant to pick up and dial a key.

## Quickstart

1. Integrate the included `docker-compose.yml`

1. Map your serial modem device to `/dev/ttyACM0`

1. Set any `environment:` variables you need, or omit them to accept the defaults

| Environment Variable | Default | Purpose |
|---|---|---|
| `DIAL` | `6` | The button to press after picking up, `0`-`9`, `*` or `#` |
| `BAUDRATE` | `57600` | The baud rate of your modem; "56k" should keep the default. |
| `TIMEOUT` | `3` | Timeout (seconds) for modem to react to commands, serial read-write. |
| `DTMF_DURATION` | `255` | Duration (miliseconds) that DTMF tones are played. |

## Complete Build

```bash
# Get the latest python base image
docker pull python:3.9-alpine

# Build a local image
docker build -t dtmf-butler .

# Run it
docker run -it --rm --user=root --device=/dev/ttyACM0 --name=dtmf-butler dtmf-butler
```

## References

- https://michaelgellis.tripod.com/modem.html
- https://www.cmrr.umn.edu/~strupp/serial.html#modems
- https://en.wikibooks.org/wiki/Serial_Programming/Modems_and_AT_Commands
- https://en.wikipedia.org/wiki/Voice_modem_command_set
- https://en.wikipedia.org/wiki/Hayes_command_set

## Other cool projects

- https://iotbytes.wordpress.com/usb-analog-modem-with-raspberry-pi/
- https://iotbytes.wordpress.com/send-dtmf-tones-with-raspberry-pi
- https://github.com/stanzheng/home-rotary-doorbot by @stanzheng
