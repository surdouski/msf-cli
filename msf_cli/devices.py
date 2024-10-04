import time
import ssl
import sys
import os

import click
from rich.console import Console
from rich.table import Table
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from sniffs import Sniffs

load_dotenv(".config")
load_dotenv(".secrets")

console = Console()
devices_dict = {}
sniffs = Sniffs()


class Clr:
    loc = "orange1"
    dev = "chartreuse3"
    set = "cyan1"
    val = "magenta"


@click.group()
def dops():
    """Device Operations Command Line Interface"""
    pass


@dops.command()
@click.argument("device_id", required=False)
@click.argument("setting_id", required=False)
@click.option("--set", "-s", "new_value", help="Value to publish/set.")
def devices(device_id, setting_id, new_value):
    """
    Shows device settings, or updates a specific device setting.

    \b
    Usage:
    dops devices
    dops devices <device_id>
    dops devices <device_id> <setting_id>
    dops devices <device_id> <setting_id> [--set]/[-s] <value> [--type]/[-t] <_type>
    """

    print_settings_string = ""
    def add_print_setting(setting_key: str, setting_value: str):
        nonlocal print_settings_string
        print_settings_string += f"[orange3]{setting_key}[/orange3][magenta]:[/magenta] [bright_white]{setting_value}[magenta];[/magenta] "

    # load_dotenv(".config")
    _devices_topic = os.getenv("MQTT_DEVICES_TOPIC", "test/devices")
    add_print_setting("MQTT_DEVICES_TOPIC", _devices_topic)

    # load_dotenv(".secrets")
    _user = os.getenv("MQTT_SERVER_USER")
    if _user:
        add_print_setting("MQTT_SERVER_USER", _user)
    _password = os.getenv("MQTT_SERVER_PASS")
    _host = os.getenv("MQTT_SERVER_HOST", "localhost")
    add_print_setting("MQTT_SERVER_HOST", _host)
    _port = int(os.getenv("MQTT_SERVER_PORT", 1883))
    add_print_setting("MQTT_SERVER_PORT", _port)

    if _user and not _password:
        console.print(
            f"[bold red]Error: Must set MQTT_SERVER_PASSWORD if MQTT_SERVER_USER is set.[/bold red]")
        sys.exit(1)

    console.print(print_settings_string)

    # Setup MQTT
    def run_client() -> mqtt.Client:
        nonlocal client
        client = mqtt.Client(client_id="dops_client")
        if _user and _password:
            client.username_pw_set(_user, password=_password)
            client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.connect(_host, _port)
        sniffs.bind(client)
        client.loop_start()
        time.sleep(0.5)  # Short delay
        client.loop_stop()
        return client

    # Define MQTT routes within the command
    @sniffs.route(_devices_topic.rstrip("/").lstrip("/") + "/<device_id>/<setting>/<config>:{type,description,value}")
    def client_reported_device_setting_value(device_id, setting, config, message):
        if isinstance(message, bytes):
            message = message.decode()
        if device_id not in devices_dict:
            devices_dict[device_id] = {}
        if setting not in devices_dict[device_id]:
            devices_dict[device_id][setting] = {}

        if config == "type":
            devices_dict[device_id][setting]["type"] = message
        elif config == "description":
            devices_dict[device_id][setting]["description"] = message
        elif config == "value":
            devices_dict[device_id][setting]["client_reported_value"] = message

    # Define MQTT routes within the command
    @sniffs.route(_devices_topic.rstrip("/").lstrip("/") + "/<device_id>/<setting>/value/reported")
    def self_reported_device_setting_value(device_id, setting, message):
        if isinstance(message, bytes):
            message = message.decode()
        if device_id not in devices_dict:
            devices_dict[device_id] = {}
        if setting not in devices_dict[device_id]:
            devices_dict[device_id][setting] = {}
        devices_dict[device_id][setting]["device_reported_value"] = message

    # devices_dict structure
    """
    {
        "device_name": {
            "setting_name": {
                "type": "int",
                "description": "the description",
                "client_reported_value": "foo",
                "device_reported_value": "bar"
            }
        }
    }
    """

    # Call the client
    client = run_client()

    is_command_list_devices = not device_id
    is_command_get_device = not setting_id
    is_command_set_device_setting = bool(new_value)
    is_command_get_device_setting = not is_command_get_device and not is_command_set_device_setting

    if is_command_list_devices:
        if not devices_dict:
            console.print(f"No devices found at [{Clr.loc}]{_devices_topic}[/{Clr.loc}].")
            return

        table = Table()
        table.add_column("Devices", style=Clr.dev)
        for device_id in devices_dict:
            table.add_row(device_id)
        console.print(table)
        return

    device = devices_dict.get(device_id)
    if not device:
        console.print(
            f"Device: [{Clr.dev}]{device_id}[/{Clr.dev}] not found at [{Clr.loc}]{_devices_topic}[/{Clr.loc}].")
        return

    if is_command_get_device_setting or is_command_set_device_setting:
        if not device.get(setting_id):
            console.print(
                f"Device: [{Clr.dev}]{device_id}[/{Clr.dev}] and setting: [{Clr.set}]{setting_id}[/{Clr.set}] not found at [{Clr.loc}]{_devices_topic}[/{Clr.loc}].")
            return

    if is_command_get_device:
        table = Table(title=f"Device: [{Clr.dev}]{device_id}[/{Clr.dev}]")
        table.add_column("Setting", style=Clr.set)
        table.add_column("Value", style=Clr.val)
        table.add_column("Type", style=Clr.val)
        table.add_column("Description", style=Clr.val)
        for setting, setting_dict in device.items():
            client_reported = setting_dict.get("client_reported_value")
            device_reported = setting_dict.get("device_reported_value")
            value = client_reported if client_reported else device_reported
            table.add_row(setting, value, setting_dict.get("type"), setting_dict.get("description"))
        console.print(table)

    elif is_command_get_device_setting:
        table = Table(title=f"Device: [{Clr.dev}]{device_id}[/{Clr.dev}]")
        table.add_column("Setting", style=Clr.set)
        table.add_column("Value", style=Clr.val)
        table.add_column("Type", style=Clr.val)
        table.add_column("Description", style=Clr.val)

        # table.add_row(setting_id, device.get(setting_id))
        setting_dict = device.get(setting_id)
        client_reported = setting_dict.get("client_reported_value")
        device_reported = setting_dict.get("device_reported_value")
        value = client_reported if client_reported else device_reported
        table.add_row(setting_id, value, setting_dict.get("type"), setting_dict.get("description"))

        console.print(table)

    elif is_command_set_device_setting:
        topic = f"{_devices_topic}/{device_id}/{setting_id}/value"
        client.publish(topic, new_value, retain=True)
        client.loop_start()
        time.sleep(0.5)
        client.loop_stop()

        table = Table(title=f"Device: [{Clr.dev}]{device_id}[/{Clr.dev}]")
        table.add_column("Setting", style=Clr.set)
        table.add_column("Value", style=Clr.val)
        table.add_column("Type", style=Clr.val)
        table.add_column("Description", style=Clr.val)

        setting_dict = device.get(setting_id)
        client_reported = setting_dict.get("client_reported_value")
        device_reported = setting_dict.get("device_reported_value")
        value = client_reported if client_reported else device_reported
        table.add_row(setting_id, value, setting_dict.get("type"), setting_dict.get("description"))

        console.print(table)


if __name__ == "__main__":
    dops()
