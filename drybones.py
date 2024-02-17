# CLI design guidelines:
# - https://clig.dev/
# - https://blog.developer.atlassian.com/10-design-principles-for-delightful-clis/


import click
import sys
import os
import shutil
import yaml

from _version import __version__

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
    cwd = os.getcwd()
    config_dir = os.path.join(cwd, CONFIG_DIR_NAME)
    project_config_fp = get_project_config_fp_from_config_dir(config_dir)
    existing_project_name = get_project_name_from_config_dir(config_dir)
    click.echo(f"Project '{existing_project_name}' at {config_dir}", err=True)


@click.command(name="show")
def project_show():
    """Show the name and location of the current project."""
    print_current_project()
project.add_command(project_show)


@click.command(name="create")
@click.argument("project_name")
def project_create(project_name):
    """Create a new project in the current directory."""
    cwd = os.getcwd()
    config_dir = os.path.join(cwd, CONFIG_DIR_NAME)
    if os.path.exists(config_dir):
        existing_project_name = get_project_name_from_config_dir(config_dir)
        click.echo(f"Cannot create new project here. Project '{existing_project_name}' already exists at {config_dir}", err=True)
        return
    os.mkdir(config_dir)
    d = {"project-name": project_name}
    config_fp = get_project_config_fp_from_config_dir(config_dir)
    with open(config_fp, 'w') as outfile:
        yaml.dump(d, outfile, default_flow_style=False)
    click.echo(f"Created new project at {config_dir}.", err=True)
project.add_command(project_create)


def get_project_config_fp_from_config_dir(config_dir):
    return os.path.join(config_dir, "project.yaml")


def get_project_name_from_config_dir(config_dir):
    project_config_fp = get_project_config_fp_from_config_dir(config_dir)
    if not os.path.exists(project_config_fp):
        click.echo(f"Project at {config_dir} is misconfigured because it does not have a configuration file.", err=True)
        return None
    with open(project_config_fp) as f:
        contents = yaml.safe_load(f)
    try:
        return contents["project-name"]
    except KeyError:
        click.echo(f"Project at {config_dir} is misconfigured because its configuration file does not specify `project-name`.", err=True)
        return None


@click.command(name="delete")
def project_delete():
    """Delete the project in the current directory."""
    # this won't delete the text files from the project dir, it will just make DryBones forget this project exists by removing it from the config files that tell it where to look
    # so you would have to redo the project-specific configuration if you wanted to reinstate it, but the data would all still be there
    cwd = os.getcwd()
    config_dir = os.path.join(cwd, CONFIG_DIR_NAME)
    project_config_fp = get_project_config_fp_from_config_dir(config_dir)
    existing_project_name = get_project_name_from_config_dir(config_dir)
    click.echo(f"Deleting project '{existing_project_name}' will remove the configuration files at {config_dir}, but will not remove any of the other files in this directory.\nAre you sure you want to continue deleting this project? Enter 'yes' to continue. Any other response will abort the operation.", err=True)
    response = input()
    if response == "yes":
        click.echo("Deleting project...", err=True)
        shutil.rmtree(config_dir)
        click.echo(f"Successfully deleted project '{existing_project_name}'.", err=True)
    else:
        click.echo("Aborting.", err=True)
project.add_command(project_delete)


if __name__ == '__main__':
    main(prog_name=PROG_NAME_FOR_COMMAND)

