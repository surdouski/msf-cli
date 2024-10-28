# MSF CLI

The MSF CLI tool is designed for creating and managing projects using the MicroPython Sniffs Framework (MSF). You can find the framework repository here: https://github.com/surdouski/micropython-sniffs-framework.

## Installation

```bash
pipx install msf-cli
```

## Usage

> Note: Note: Docker must be installed and available in your system path for broker commands to function.

### new

```bash
msf new <path>               # creates new msf project at <path>
```

The `new` command initializes a new project at `<path>`. It provides a convenient setup for starting development, including essential configuration files such as `.config/mqtt_as.json`, with default settings (note: updating the "server" field is necessary). Additionally, the framework and required dependencies are installed.

Example directory structure after running this command:

![new-cmd.png](new-cmd.png)

Once configuration is updated, you can uncomment relevant code in `main.py` to test the device and settings setup. To run this, navigate to the project path, execute `mpbridge dev a0`, wait for initialization, press `<Enter>`, then press `<Ctrl+D>` for a soft restart to execute `main.py`.

### install

```bash
msf install <package>
```

This command installs a MicroPython package to the "lib" directory in the current working directory, creating "lib" if it does not exist. Package names follow the syntax expected by `mpremote`.

Examples:

```bash
msf install pathlib
msf install github:surdouski/micropython-sniffs
```

### broker

```bash
msf broker up --port=1883    # starts a local MQTT broker for testing (--port is optional, default is 1883)
msf broker down              # stops the local MQTT broker
```

#### up

```bash
msf broker up
# output: Local MQTT broker started at 192.168.x.x:1883.
```

This command sets up a local MQTT broker for testing within your network. If you have an existing broker, feel free to use it instead.

The command launches an `eclipse-mosquitto:1.6` Docker container with default settings. You can use the optional `--port` parameter to specify a custom port. The command will output your local network IP and port information for connection.

#### down

```bash
msf broker down
```

Stops and removes the MQTT broker container.


### devices

Device configurations and secrets can be passed as environment variables on the command line:

```bash
MQTT_DEVICES_TOPIC=test/devices msf devices <cmd>
```

Alternatively, you can specify configurations in two files: `.config` and `.secrets`.

_.config_
```
MQTT_DEVICES_TOPIC=topic/path/to/devices
```

_.secrets_
```
MQTT_SERVER_HOST=localhost
MQTT_SERVER_PORT=1883
MQTT_SERVER_USER=myuser  # optional
MQTT_SERVER_PASS=mypass  # optional, but required if user is specified
```

#### list


```bash
# list devices
msf devices
```

![devices-list.png](devices-list.png)


#### get device

```bash
# list settings for a device
msf devices <device_id>
```

![get-device_id.png](get-device_id.png)

#### get device setting

```bash
# show a specific setting
msf devices <device_id> <setting_id>
```

![get-device-setting.png](get-device-setting.png)

#### set device setting

```bash
# update the value of a setting
msf devices <device_id> <setting_id> [--set]/[-s] <value>
```

![set-device-setting.png](set-device-setting.png)

## Tests (Development)

A test harness for this project is planned for future inclusion in workflows.