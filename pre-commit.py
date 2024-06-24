import json
import logging
import platform
import subprocess
import sys
from collections.abc import Sequence
from typing import LiteralString, TextIO

import click

logging.basicConfig(format='%(message)s', level=logging.INFO)


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


@scripts.command(help='Check coverage total percent, using json file.')
@click.argument('file', type=click.File('r'), nargs=1)
@click.option(
    '--expected-coverage',
    '-e',
    default=30,
    type=int,
    help=(
        'Expected coverage percent. If actual coverage will lower that this '
        'value, script return error, default is 60.'
    ),
)
def coverage(file: TextIO, expected_coverage: int) -> None:
    """Check coverage total percent, using "coverage.json".

    After run command "pytest --cov --cov-report json" file "coverage.json"
     will create. This script parse it and compare with desire coverage
     percent value.
    :param TextIO file: json file.
    :param int expected_coverage: expected coverage percent.
    :returns: None
    """
    parsed = json.load(file)
    total = int(parsed['totals']['percent_covered'])
    if total < expected_coverage:
        logging.error(
            'Your coverage %s%% is lower than %s%%',
            total,
            expected_coverage,
        )
        sys.exit(1)
    logging.info('Coverage %s%% is fine', total)


if __name__ == '__main__':
    scripts()
