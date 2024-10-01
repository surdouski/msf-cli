import click
import os
import subprocess
import shutil


def check_docker_installed():
    """Check if docker is installed and available on PATH."""
    if shutil.which('docker') is None:
        click.echo("Error: Docker is not installed or not available on PATH.")
        return False
    return True

@click.group()
def cli():
    """MSF CLI - A command-line tool for creating and managing MSF projects."""
    pass

@click.command()
@click.argument('path', type=click.Path())
def new(path):
    """Creates a new MSF project at the given <path>."""
    try:
        os.makedirs(path)
        click.echo(f"New MSF project created at {path}.")
    except FileExistsError:
        click.echo(f"Error: Directory {path} already exists.")
    except Exception as e:
        click.echo(f"Error: {e}")

@click.group()
def broker():
    """Commands for managing a local MQTT broker."""
    pass

@broker.command('up')
@click.option('--port', default=1883, help='Local port for the MQTT broker (default is 1883).')
def broker_up(port: int):
    """Starts a local MQTT broker."""
    if not check_docker_installed():
        return
    try:
        subprocess.run(['docker', 'run', '-d', '-p', f'{port}:1883', '--name', 'mosquitto', 'eclipse-mosquitto:1.6'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        ip_address = subprocess.check_output("hostname -I | awk '{print $1}'", shell=True).decode().strip()
        click.echo(f"Local MQTT broker started at {ip_address}:{port}.")
    except subprocess.CalledProcessError:
        click.echo("Error starting MQTT broker.")

@broker.command('down')
def broker_down():
    """Stops the local MQTT broker."""
    if not check_docker_installed():
        return
    try:
        subprocess.run(['docker', 'stop', 'mosquitto'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        subprocess.run(['docker', 'rm', 'mosquitto'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        click.echo("Local MQTT broker stopped and removed.")
    except subprocess.CalledProcessError:
        click.echo("Error stopping or removing MQTT broker.")

# Add commands to the main CLI group
cli.add_command(new)
cli.add_command(broker)

if __name__ == '__main__':
    cli()
