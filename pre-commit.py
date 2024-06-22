import logging
import platform
import subprocess
import sys
from collections.abc import Sequence
from typing import LiteralString

import click

logging.basicConfig(format='%(message)s', level=logging.INFO)
logging.info('Current system: %s', platform.system())


def run_subprocess_command(command: Sequence[LiteralString]) -> str:
    """Run any command as subprocess of this script.

    :param str command: command that needs run as subprocess.
    :returns: stdout output.:
    """
    use_shell = platform.system() == 'Windows'
    result = subprocess.run(
        command,
        shell=use_shell,  # noqa: S603
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        logging.error(result.stderr.decode('utf-8'))
        sys.exit(result.returncode)
    return result.stdout.decode('utf-8')


@click.group(help='Scripts for local pre-commit hooks.')
def scripts() -> None:
    """Group for scripts for local pre-commit hooks."""


@scripts.command(help='Checking updated for dependencies.')
def check_updates() -> None:
    """Check updates of dependencies.

    :returns: None
    """
    output = run_subprocess_command(
        ('pip', 'list', '--outdated', '--exclude', 'pydantic-core'),
    )
    if output:
        logging.warning(output)
        sys.exit(1)


if __name__ == '__main__':
    scripts()
