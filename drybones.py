# CLI design guidelines:
# - https://clig.dev/
# - https://blog.developer.atlassian.com/10-design-principles-for-delightful-clis/


import click

from _version import __version__


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
VERSION_MESSAGE = "%(prog)s, version %(version)s\nSource: https://github.com/Kuhron/drybones"


def add_help(f):
    help_option_dec = click.option("-h", "--help", "show_help", is_flag=True, help="Show help and exit.")
    name_str = f.__name__
    doc_str = f.__doc__
    def f2(*args, show_help=False, **kwargs):
        if show_help:
            # ignore everything else and show help and exit
            help([name_str])  # need list since Click is calling `args = list(args)` and it will splat the string if you just pass the command name directly
            return
        f(*args, **kwargs)
    f2 = help_option_dec(f2)
    f2.__name__ = name_str
    f2.__doc__ = doc_str
    return f2


def print_help(ctx=None, subcommand=None):
    if ctx is None:
        ctx = click.get_current_context()
    if subcommand is not None:
        if type(subcommand) is not click.Command:
            print(f"can't print help for non-Command object {subcommand = }")
            return
    click.echo(subcommand.get_help(ctx))
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name', help='The person to greet.')
@click.version_option(__version__, "-v", "--version", prog_name="DryBones", message=VERSION_MESSAGE)
def main():
    """Welcome to DryBones, a tool for parsing linguistic texts in the command line.\n
    Author: Wesley Kuhron Jones\n
    Source: https://github.com/Kuhron/drybones"""
    pass


@click.command
@add_help
def example():
    """This is an example subcommand."""
    # example subcommand so one can type `dry subcommand` in a git-like fashion
    click.echo("this is a subcommand")
main.add_command(example)


@click.command
@click.argument("subcommand")
def help(subcommand=None):
    """This is the help subcommand."""
    # TODO at some point (low priority), would be nice to have the help messages for `example` subcommand all show usage with `dry example ...` rather than just `example`. `dry help example` shows `dry example ...` but `dry example -h` and `dry example --help` only show `example ...`
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


if __name__ == '__main__':
    main(prog_name="dry")

