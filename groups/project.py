# things related to keeping track of the whole project in a directory
# creating, deleting, renaming, etc., high-level admin like that

import click
import os
import yaml
import shutil

import ProjectUtil as ju


@click.group(no_args_is_help=True)
def project():
    """Create and manage projects."""
    # projects are like separate corpora, like how each language has its own FLEx project
    # confine them to local dirs like how git does
    pass


@click.pass_context
def print_current_project(ctx):
    cwd = os.getcwd()
    config_dir = os.path.join(cwd, ctx.obj.config_dir_name)
    project_config_fp = ju.get_project_config_fp_from_config_dir(config_dir)
    existing_project_name = ju.get_project_name_from_config_dir(config_dir)
    if existing_project_name is not None:
        click.echo(f"Project '{existing_project_name}' at {config_dir}", err=True)


@click.command(name="show")
def project_show():
    """Show the name and location of the current project."""
    print_current_project()
project.add_command(project_show)


@click.command(name="create")
@click.argument("project_name")
@click.pass_context
def project_create(ctx, project_name):
    """Create a new project in the current directory."""
    cwd = os.getcwd()
    config_dir = os.path.join(cwd, ctx.obj.config_dir_name)
    if os.path.exists(config_dir):
        existing_project_name = ju.get_project_name_from_config_dir(config_dir)
        click.echo(f"Cannot create new project here. Project '{existing_project_name}' already exists at {config_dir}", err=True)
        return
    os.mkdir(config_dir)
    d = {"project-name": project_name}
    config_fp = ju.get_project_config_fp_from_config_dir(config_dir)
    with open(config_fp, 'w') as outfile:
        yaml.dump(d, outfile, default_flow_style=False)
    click.echo(f"Created new project at {config_dir}.", err=True)
project.add_command(project_create)


@click.command(name="delete")
@click.pass_context
def project_delete(ctx):
    """Delete the project in the current directory."""
    # this won't delete the text files from the project dir, it will just make DryBones forget this project exists by removing it from the config files that tell it where to look
    # so you would have to redo the project-specific configuration if you wanted to reinstate it, but the data would all still be there
    cwd = os.getcwd()
    config_dir = os.path.join(cwd, ctx.obj.config_dir_name)
    project_config_fp = ju.get_project_config_fp_from_config_dir(config_dir)
    existing_project_name = ju.get_project_name_from_config_dir(config_dir)
    if existing_project_name is None:
        return
    click.echo(f"Deleting project '{existing_project_name}' will remove the configuration files at {config_dir}, but will not remove any of the other files in this directory.\nAre you sure you want to continue deleting this project? Enter 'yes' to continue. Any other response will abort the operation.", err=True)
    response = input()
    if response == "yes":
        click.echo("Deleting project...", err=True)
        shutil.rmtree(config_dir)  # BE VERY CAREFUL THAT THIS IS THE CORRECT DIR
        click.echo(f"Successfully deleted project '{existing_project_name}'.", err=True)
    else:
        click.echo("Aborting.", err=True)
project.add_command(project_delete)