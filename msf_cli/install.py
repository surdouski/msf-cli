import os
import subprocess
from pathlib import Path

import click


@click.command()
@click.argument('package')
def install(package):
    """Installs a micropython package and it's dependencies in the cwd's 'lib' directory."""
    try:
        cwd = Path(os.getcwd())

        # Use micropython/unix Docker image to install the libraries to /lib
        install_to_lib = [
            "docker",
            "run",
            "--rm",
            "-v", f"{cwd.absolute()}/lib:/root/.micropython/lib",
            "micropython/unix",
            "micropython",
            "-m", "mip", "install", f"{package}"
        ]
        subprocess.run(install_to_lib, check=True)

        # Need to fix the permissions afterward because we need access to `/root/` in the container
        chown_command = [
            "sudo",
            "chown",
            "-R",
            f"{subprocess.check_output(['whoami']).decode().strip()}:{subprocess.check_output(['whoami']).decode().strip()}",
            f"{(cwd / 'lib').absolute()}"
        ]
        subprocess.run(chown_command, check=True)

        click.echo(f"Installed {package}.")

    except Exception as e:
        click.echo(f"Error: {e}")
