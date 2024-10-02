import click
from pathlib import Path
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
        project_path = Path(path)

        config_dir = project_path / '.config'
        config_dir.mkdir(parents=True, exist_ok=True)

        # Define source files from the 'static' directory in the click application
        base_dir = Path(__file__).parent  # Get the directory of this script
        static_dir = base_dir / 'static'
        mqtt_as_src = static_dir / 'mqtt_as.json'
        main_src = static_dir / 'main.py'
        settings_src = static_dir / 'settings.py'
        mpbridge_ignore_src = static_dir / 'mpbridge.ignore'

        # Define destination paths
        mqtt_as_dest = config_dir / 'mqtt_as.json'
        main_dest = project_path / 'main.py'
        settings_dest = project_path / 'settings.py'
        mpbridge_ignore_dest = project_path / 'mpbridge.ignore'

        mqtt_as_dest.write_bytes(mqtt_as_src.read_bytes())
        main_dest.write_bytes(main_src.read_bytes())
        settings_dest.write_bytes(settings_src.read_bytes())
        mpbridge_ignore_dest.write_bytes(mpbridge_ignore_src.read_bytes())

        # Use micropython/unix Docker image to install the libraries to /lib
        install_msf_to_lib = [
            "docker",
            "run",
            "--rm",
            "-v", f"{project_path.absolute()}/lib:/root/.micropython/lib",
            "micropython/unix",
            "micropython",
            "-m", "mip", "install", "github:surdouski/micropython-sniffs-framework"
        ]
        subprocess.run(install_msf_to_lib, check=True)

        # Need to fix the permissions afterward because we need access to `/root/` in the container
        chown_command = [
            "sudo",
            "chown",
            "-R",
            f"{subprocess.check_output(['whoami']).decode().strip()}:{subprocess.check_output(['whoami']).decode().strip()}",
            f"{(project_path / 'lib').absolute()}"
        ]
        subprocess.run(chown_command, check=True)

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
