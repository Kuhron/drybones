# getting information about the current project and its texts
# put helper functions here that are not actual commands in the "project" subcommand group


import click
import os
import yaml



def get_project_config_fp_from_config_dir(config_dir):
    return os.path.join(config_dir, "project.yaml")


def get_project_name_from_config_dir(config_dir):
    if not os.path.exists(config_dir):
        click.echo(f"No DryBones project found here. Expected configuration directory at {config_dir}", err=True)
        return None
    project_config_fp = get_project_config_fp_from_config_dir(config_dir)
    if not os.path.exists(project_config_fp):
        click.echo(f"Project at {config_dir} is misconfigured because it does not have a configuration file. Expected configuration file at {project_config_fp}", err=True)
        return None
    with open(project_config_fp) as f:
        contents = yaml.safe_load(f)
    try:
        return contents["project-name"]
    except KeyError:
        click.echo(f"Project at {config_dir} is misconfigured because its configuration file does not specify `project-name`. Configuration file is located at {project_config_fp}", err=True)
        return None


def get_text_names():
    # should use info about the project's home dir or just cwd?
    cwd = os.getcwd()

    # maybe should have DryBones keep track of which files are actual texts and which are not instead of inferring it from the file name/contents
    # but for now, keep it simple
    txt_fnames = [x for x in os.listdir(cwd) if x.endswith(".txt")]
    return [os.path.splitext(fname)[0] for fname in txt_fnames]
