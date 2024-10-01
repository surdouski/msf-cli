# MSF Cli

For use in creating and managing a project using the micropython-sniffs-framework: https://github.com/surdouski/micropython-sniffs-framework.

## Installation

```bash
pipx install msf-cli
```

## Usage

Note: docker must be installed and on path for broker commands.

```bash
msf new <path>               # creates new msf project at <path>
msf broker up --port=1883    # starts a local MQTT broker for testing (--port is optional, default is 1883)
msf broker down              # stops the local MQTT broker
```

### $ msf new path

Not implemented yet, just creates a new empty directory at path at the moment.

### $ msf broker up

This command is meant for testing on your local network. If you already have a broker set up elsewhere that
you want to use, use that instead.

This command runs a `eclipse-mosquitto:1.6` container with some defaults. Can optionally add `--port` to specify
a different port on your local machine you want to access it through.

This command also outputs your IP and port you can connect to it through on your local network.

```bash
msf broker up
# output: Local MQTT broker started at 192.168.x.x:1883.
```

### msf broker down

Stops and removes the broker.