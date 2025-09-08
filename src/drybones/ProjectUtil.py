# getting information about the current project and its texts
# put helper functions here that are not actual commands in the "project" subcommand group

# TODO figure out how to put info like this in the docs for subcommands, or man pages, or online docs, or all of the above
# "current" means you are already in the project's directory, e.g. "Daool" for the project named "Daool", and the directory ".drybones" is a direct child of the cwd
# getting things from project name means you are going to create or look into a direct child directory of the cwd, and this child's name is the project name and it is the project dir


import click
import os
import yaml
from pathlib import Path

from drybones.Constants import DRYBONES_DIR_NAME


@click.pass_context
def get_project_config_fp_from_project_name(ctx, project_name:str, parent_dir:Path|None=None) -> Path:
    drybones_dir = get_drybones_dir_from_project_name(ctx, project_name=project_name, parent_dir=parent_dir)
    return drybones_dir / ctx.obj.project_config_file_name


@click.pass_context
def get_project_config_fp_from_drybones_dir(ctx, drybones_dir:Path) -> Path:
    return drybones_dir / ctx.obj.project_config_file_name


@click.pass_context
def get_drybones_dir_from_project_name(ctx, project_name:str, parent_dir:Path|None=None) -> Path:
    project_dir = get_project_dir_from_project_name(project_name=project_name, parent_dir=parent_dir)
    return project_dir / ctx.obj.drybones_dir_name


@click.pass_context
def get_project_name_from_drybones_dir(ctx, drybones_dir:Path) -> str | None:
    if not drybones_dir.exists():
        click.echo(f"No DryBones project found here. Expected directory at {drybones_dir}", err=True)
        return None
    project_config_fp = get_project_config_fp_from_drybones_dir(ctx, drybones_dir)
    if not project_config_fp.exists():
        click.echo(f"Project at {drybones_dir} is misconfigured because it does not have a configuration file. Expected configuration file at {project_config_fp}", err=True)
        return None
    with open(project_config_fp) as f:
        contents = yaml.safe_load(f)
    try:
        return contents["project-name"]
    except KeyError:
        click.echo(f"Project at {drybones_dir} is misconfigured because its configuration file does not specify `project-name`. Configuration file is located at {project_config_fp}", err=True)
        return None


def get_project_dir_from_project_name(project_name:str, parent_dir:Path|None=None) -> Path:
    if parent_dir is None:
        parent_dir = Path.cwd()
    return parent_dir / project_name


@click.pass_context
def get_project_drybones_dir_from_project_name(ctx, project_name:str, parent_dir:Path|None=None) -> Path:
    project_dir = get_project_dir_from_project_name(project_name=project_name, parent_dir=parent_dir)
    return project_dir / ctx.obj.drybones_dir_name


@click.pass_context
def print_current_project(ctx):
    drybones_dir = get_current_drybones_dir(ctx)
    existing_project_name = get_project_name_from_drybones_dir(ctx, drybones_dir)
    if existing_project_name is not None:
        click.echo(f"Project '{existing_project_name}' at {drybones_dir}", err=True)


@click.pass_context
def current_project_exists(ctx) -> bool:
    return get_current_drybones_dir(ctx).exists()


@click.pass_context
def project_exists(ctx, project_name:str) -> bool:
    return get_drybones_dir_from_project_name(ctx, project_name=project_name).exists()


@click.pass_context
def get_current_drybones_dir(ctx) -> Path:
    cwd = Path.cwd()
    drybones_dir = cwd / ctx.obj.drybones_dir_name
    return drybones_dir


@click.pass_context
def get_current_project_config_fp(ctx) -> Path:
    drybones_dir = get_current_drybones_dir(ctx)
    config_fp = drybones_dir / ctx.obj.project_config_file_name
    return config_fp


@click.pass_context
def create_project(ctx, project_name:str) -> None:
    drybones_dir = get_drybones_dir_from_project_name(ctx, project_name=project_name)
    drybones_dir.mkdir(parents=True)
    config_fp = get_project_config_fp_from_drybones_dir(ctx, drybones_dir=drybones_dir)
    project_metadata = {"project-name": project_name}
    with open(config_fp, 'w') as outfile:
        yaml.dump(project_metadata, outfile, default_flow_style=False)
    click.echo(f"Created new project {project_name!r}.", err=True)


def get_closest_parent_drybones_dir(fp:Path, raise_if_none:bool=False) -> Path | None:
    fp = fp.absolute()

    # if it's a file, get the dir it's in
    # if it's a dir, check itself first
    if fp.is_file():
        p = fp.parent
    else:
        p = fp
    
    limit = 10000
    limiter = 0
    while limiter < limit:
        drybones_dir = p / DRYBONES_DIR_NAME
        if drybones_dir.exists():
            return drybones_dir
        if is_filesystem_root(p):
            # we went all the way up without finding any .drybones dir
            break
        p = p.parent
        limiter += 1
    
    # none found
    if raise_if_none:
        click.echo("No .drybones dir was found here or in any parent directories.", err=True)
        raise click.Abort()
    else:
        return None


def get_corpus_dir(drybones_fp:Path) -> Path:
    # get the dir in which we should glob for .dry files from which to get existing parses/glosses
    d2 = get_closest_parent_drybones_dir(drybones_fp)
    if d2 is None:
        # just use .dry files in the dir with this file
        return drybones_fp.parent
    else:
        assert d2.name == ".drybones", d2.name
        return d2.parent


def is_filesystem_root(p:Path) -> bool:
    return p == p.parent

