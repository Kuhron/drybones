import click
import sys
import os
import shutil
import yaml

from _version import __version__
from GenericObject import GenericObject


STDIN_IS_TTY = sys.stdin.isatty()
STDOUT_IS_TTY = sys.stdout.isatty()
STDERR_IS_TTY = sys.stderr.isatty()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
PROG_NAME_FOR_VERSION = "DryBones"
PROG_NAME_FOR_COMMAND = "dry"
VERSION_MESSAGE = "%(prog)s, version %(version)s\nSource: https://github.com/Kuhron/drybones"
HOME_DIR = os.environ["HOME"]
CONFIG_DIR_NAME = ".drybones"
GLOBAL_CONFIG_FP = os.path.join(HOME_DIR, ".drybones.conf")
if not os.path.exists(GLOBAL_CONFIG_FP):
    open(GLOBAL_CONFIG_FP, "w").close()

DEFAULT_ALIGNED_ROWS = ["Bl", "Mp", "Lx", "Gl", "Wc"]


@click.group(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name', help='The person to greet.')
@click.version_option(__version__, "-v", "--version", prog_name=PROG_NAME_FOR_VERSION, message=VERSION_MESSAGE)
@click.pass_context
def main(ctx):
    """Welcome to DryBones, a tool for parsing linguistic texts in the command line.\n
    Author: Wesley Kuhron Jones\n
    Source: https://github.com/Kuhron/drybones"""
    ctx.obj = GenericObject()
    ctx.obj.config_dir_name = CONFIG_DIR_NAME
    ctx.obj.labels_of_aligned_rows = DEFAULT_ALIGNED_ROWS


@click.command
def example():
    """This is an example subcommand."""
    # example subcommand so one can type `dry subcommand` in a git-like fashion
    click.echo("this is a subcommand")
main.add_command(example)


@click.command
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


@click.command
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

from groups.config import config as config_group
from groups.project import project as project_group
from groups.read import read as read_group

main.add_command(config_group)
main.add_command(project_group)
main.add_command(read_group)



if __name__ == '__main__':
    # make sure you are working in drybones virtualenv!
    # if not, you might get AttributeError: 'function' object has no attribute 'name'

    main(prog_name=PROG_NAME_FOR_COMMAND)
