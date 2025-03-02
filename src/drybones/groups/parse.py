# things relating to parsing texts

import click


@click.command
@click.argument("text_name")
@click.argument("line_number", required=False, type=int)
@click.pass_context
def parse(ctx, text_name, line_number):
    """Parse text contents."""
    click.echo("parse not implemented", err=True)

