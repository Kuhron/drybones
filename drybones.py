# CLI design guidelines:
# - https://clig.dev/
# - https://blog.developer.atlassian.com/10-design-principles-for-delightful-clis/


import click
import sys
import os

from _version import __version__

STDIN_IS_TTY = sys.stdin.isatty()
STDOUT_IS_TTY = sys.stdout.isatty()
STDERR_IS_TTY = sys.stderr.isatty()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
PROG_NAME_FOR_VERSION = "DryBones"
PROG_NAME_FOR_COMMAND = "dry"
VERSION_MESSAGE = "%(prog)s, version %(version)s\nSource: https://github.com/Kuhron/drybones"
HOME_DIR = os.environ["HOME"]
GLOBAL_CONFIG_FP = os.path.join(HOME_DIR, ".drybones.conf")
if not os.path.exists(GLOBAL_CONFIG_FP):
    open(GLOBAL_CONFIG_FP, "w").close()


def print_help(ctx=None, subcommand=None):
    if ctx is None:
        ctx = click.get_current_context()
    if subcommand is not None:
        if type(subcommand) is not click.Command:
            click.echo(f"can't print help for non-Command object {subcommand = }", err=True)
            return
    click.echo(subcommand.get_help(ctx))
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name', help='The person to greet.')
@click.version_option(__version__, "-v", "--version", prog_name=PROG_NAME_FOR_VERSION, message=VERSION_MESSAGE)
def main():
    """Welcome to DryBones, a tool for parsing linguistic texts in the command line.\n
    Author: Wesley Kuhron Jones\n
    Source: https://github.com/Kuhron/drybones"""
    pass


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


@click.group(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)
def config():
    """View and edit config settings."""
    pass
main.add_command(config)


@click.command(name="set")
def config_set():
    """Set config variable."""
    click.echo("config_set not implemented", err=True)
config.add_command(config_set)


@click.command(name="show")
def config_show():
    """Show value of config variable."""
    click.echo("config_set not implemented", err=True)
config.add_command(config_show)

# for config, what kinds of things do I want? and might want it for multiple projects
# project dir, where the texts are
# might want a local .drybones directory and a global .drybones.conf like .gitconfig


@click.group(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)
def project():
    """Create and manage projects."""
    # projects are like separate corpora, like how each language has its own FLEx project
    # confine them to local dirs like how git does
    pass
main.add_command(project)


def print_current_project():
    click.echo("print_current_project not implemented", err=True)


@click.command(name="show")
def project_show():
    """Show the name and location of the current project."""
    print_current_project()
project.add_command(project_show)


@click.command(name="create")
@click.argument("project_name")
def project_create(project_name):
    """Create a new project."""
    click.echo("project_create not implemented", err=True)
project.add_command(project_create)


@click.command(name="delete")
@click.argument("project_name")
def project_delete(project_name):
    """Delete a project."""
    # this won't delete the text files from the project dir, it will just make DryBones forget this project exists by removing it from the config files that tell it where to look
    # so you would have to redo the project-specific configuration if you wanted to reinstate it, but the data would all still be there
    click.echo("project_delete not implemented", err=True)
project.add_command(project_delete)


if __name__ == '__main__':
    main(prog_name=PROG_NAME_FOR_COMMAND)

