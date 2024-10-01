# MSF Cli

For use in creating and managing a project using the micropython-sniffs-framework: https://github.com/surdouski/micropython-sniffs-framework.

## Installation

```bash
pipx install msf-cli
```

## Usage

```bash
msf new <path>  # creates new msf project at <path>
msf broker up     # starts a local MQTT broker (for testing)
msf broker down   # stops the local MQTT broker
```