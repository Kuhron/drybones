# things related to creating/deleting/listing texts and other basic operations on them
# NOT for parsing/editing

import click


@click.group(no_args_is_help=True)
def text():
    """Create and manage texts within a project."""
    pass


@click.command(name="create")
@click.argument("text_name")
@click.pass_context
def text_create(ctx, text_name):
    pass
text.add_command(text_create)

