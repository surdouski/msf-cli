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

Creates a new project at `<path>`. This is a convenience utility to set up your project so that it's easy to begin
development. However, it does also include some of the things you do require, such as the `.config/mqtt_as.json`
file with some defaults (although at minimum you need to update the "server" value). It also installs the framework and
it's required dependencies.

An example of what the directory looks like after being run:

![img.png](img.png)

After updating the json, you can uncomment
out the code in `main.py` related to the device and settings setup to test that everything is working. A simple way to
do this is to navigate to the project path, do `mpbridge dev a0`, wait for everything to load then press `<Enter>` once,
then press `<ctrl+d>` to do a soft restart on the device so that it runs `main.py`.

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

### $ msf broker down

Stops and removes the broker.

## Tests (Development)

Will eventually put up a test harness for this and add it to workflows. Today, however, is not that day.