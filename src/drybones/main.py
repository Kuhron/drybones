import click
import sys
import os
import readline  # for terminal-like input navigation using arrow keys
import shutil
import yaml
from pathlib import Path

from drybones._version import __version__
from drybones.DryBonesSession import DryBonesSession
from drybones.RowLabel import DEFAULT_ALIGNED_ROW_LABELS
from drybones.Constants import PROG_NAME_FOR_VERSION, PROG_NAME_FOR_COMMAND, DRYBONES_DIR_NAME, GLOBAL_CONFIG_FP, HOME_DIR, PROJECT_CONFIG_FILE_NAME


STDIN_IS_TTY = sys.stdin.isatty()
STDOUT_IS_TTY = sys.stdout.isatty()
STDERR_IS_TTY = sys.stderr.isatty()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
VERSION_MESSAGE = "%(prog)s, version %(version)s\nSource: https://github.com/Kuhron/drybones"



@click.group(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name', help='The person to greet.')
@click.version_option(__version__, "-v", "--version", prog_name=PROG_NAME_FOR_VERSION, message=VERSION_MESSAGE)
@click.pass_context
def main(ctx):
    """Welcome to DryBones, a tool for parsing linguistic texts in the command line.\n
    Author: Wesley Kuhron Jones\n
    Source: https://github.com/Kuhron/drybones"""
    ctx.obj = DryBonesSession(
        drybones_dir_name = DRYBONES_DIR_NAME,
        project_config_file_name = PROJECT_CONFIG_FILE_NAME,
    )


@click.command()
@click.argument("subcommand")
def help(subcommand=None):
    """Show help for a subcommand."""
    if subcommand is None:
        print_help()
    else:
        ctx = click.get_current_context()
        ctx.info_name = subcommand
        subcommand_obj = main.get_command(ctx, subcommand)
        if subcommand_obj is None:
            click.echo(f"Error: No such command '{subcommand}'.")
            return
        print_help(ctx, subcommand_obj)
main.add_command(help)


@click.command()
def version():
    """Show DryBones version."""
    click.echo(VERSION_MESSAGE % {"prog": PROG_NAME_FOR_VERSION, "version":__version__})
main.add_command(version)


def print_help(ctx=None, subcommand=None):
    if ctx is None:
        ctx = click.get_current_context()
    if subcommand is not None:
        if type(subcommand) is not click.Command:
            click.echo(f"can't print help for non-Command object {subcommand = }", err=True)
            return
    click.echo(subcommand.get_help(ctx))
    ctx.exit()



# here add the subcommand modules to main command group

from drybones.groups.accent import accent as accent_group
from drybones.groups.analyze import analyze as analyze_group
from drybones.groups.config import config as config_group
from drybones.groups.enter import enter as enter_group
from drybones.groups.map import map as map_group
from drybones.groups.merge import merge as merge_group
from drybones.groups.parse import parse as parse_group
from drybones.groups.project import project as project_group
from drybones.groups.read import read as read_group
from drybones.groups.search import search as search_group
from drybones.groups.text import text as text_group
from drybones.groups.wrap import wrap as wrap_group

main.add_command(accent_group)
main.add_command(analyze_group)
main.add_command(config_group)
main.add_command(enter_group)
main.add_command(map_group)
main.add_command(merge_group)
main.add_command(parse_group)
main.add_command(project_group)
main.add_command(read_group)
main.add_command(search_group)
main.add_command(text_group)
main.add_command(wrap_group)


if __name__ == '__main__':
    # make sure you are working in drybones virtualenv!
    # if not, you might get AttributeError: 'function' object has no attribute 'name'

    main(prog_name=PROG_NAME_FOR_COMMAND)
