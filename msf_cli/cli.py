import click

from msf_cli.broker import broker
from msf_cli.new import new
from msf_cli.devices import devices
from msf_cli.install import install


@click.group()
def cli():
    """MSF CLI - A command-line tool for creating and managing MSF projects."""
    pass


# Add commands to the main CLI group
cli.add_command(new)
cli.add_command(broker)
cli.add_command(devices)
cli.add_command(install)

if __name__ == '__main__':
    cli()
