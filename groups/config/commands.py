# things related to the configuration of a particular project
# things stored in the local .drybones dir of a project dir

import click
import os
import yaml
import shutil


@click.group(no_args_is_help=True)
@click.pass_context
def config(ctx):
    """View and edit config settings."""
    print(f"config {ctx = }\n")
    pass


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