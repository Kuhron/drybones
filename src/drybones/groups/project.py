# things related to keeping track of the whole project in a directory
# creating, deleting, renaming, etc., high-level admin like that

import click
import os
import yaml
import shutil
from pathlib import Path

import drybones.ProjectUtil as ju


@click.group(no_args_is_help=True)
def project():
    """Create and manage projects."""
    # projects are like separate corpora, like how each language has its own FLEx project
    # confine them to local dirs like how git does
    pass


@click.command(name="show")
def project_show():
    """Show the name and location of the current project."""
    ju.print_current_project()
project.add_command(project_show)


@click.command(name="create")
@click.argument("project_name")
def project_create(project_name):
    """Create a new project."""
    if ju.current_project_exists():
        existing_project_name = ju.get_current_project_name()
        click.echo(f"Cannot create new project here. Project '{existing_project_name}' already exists.", err=True)
        return
    else:
        ju.create_project(project_name)
project.add_command(project_create)


@click.command(name="delete")
@click.argument("project_name")
def project_delete(project_name):
    """Delete a project."""
    # this won't delete the text files from the project dir, it will just make DryBones forget this project exists by removing it from the config files that tell it where to look
    # so you would have to redo the project-specific configuration if you wanted to reinstate it, but the data would all still be there

    if ju.project_exists(project_name):
        drybones_dir = ju.get_drybones_dir_from_project_name(project_name)
        existing_project_name = ju.get_project_name_from_drybones_dir(drybones_dir)
        click.echo(f"Deleting project '{existing_project_name}' will remove the configuration files at {drybones_dir}, but will not remove any of the other files in this directory.\nAre you sure you want to continue deleting this project? Enter 'yes' to continue. Any other response will abort the operation.", err=True)
        response = input()
        if response == "yes":
            click.echo("Deleting project...", err=True)
            shutil.rmtree(drybones_dir)  # BE VERY CAREFUL THAT THIS IS THE CORRECT DIR
            click.echo(f"Successfully deleted project '{existing_project_name}'.", err=True)
        else:
            click.echo("Aborting.", err=True)
    else:
        click.echo(f"No project named {project_name!r} found.", err=True)
        return
project.add_command(project_delete)

