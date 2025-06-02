import click
from pathlib import Path



@click.command
@click.argument("text_fp", required=True, type=Path)
@click.argument("line_designation", required=False, type=str)
# @click.option()
# @click.option("--shuffle", "-s", type=bool, default=False, help="Shuffle the lines during parsing.")
@click.option("--overwrite", "-o", type=bool, default=False, help="Overwrite the input file. If false, a separate file will be created.")
@click.pass_context
def merge(ctx):
    """Merge lines from two files."""
