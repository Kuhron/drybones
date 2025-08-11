# things relating to searching by string/regex in whichever rows
# this is NOT about searching for row labels themselves; it is about the row contents

import click
import os
import yaml
import shutil
from pathlib import Path

from drybones.RowLabel import RowLabel


# @click.group(no_args_is_help=True)
@click.command(no_args_is_help=True)
@click.argument("row_label")
@click.argument("query")
@click.option("--regex", "-r", type=bool, default=False, help="Search using regex.")
def search(row_label: RowLabel, query: str, regex):
    """Search row contents using string/regex match."""

    click.echo(f"Searching for {'regex' if regex else 'string'} {query!r} in rows labeled {row_label}.")

    raise NotImplementedError

