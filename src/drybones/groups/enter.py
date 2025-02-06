# things related to raw data entry of texts via the command line
# start simple and add functionality later, don't kitchen-sink one subcommand


import click
from pathlib import Path


@click.command
@click.argument("text_name")
def enter(text_name):
    """Enter raw data for a text. This can also be done manually in the text files themselves."""
    click.echo(f"Now entering data for text {text_name!r}. Press Ctrl+C to cancel current command, Ctrl+D to exit.")
    # TODO figure out how to get the Ctrl+C and Ctrl+D behavior to work with Click exceptions: https://click.palletsprojects.com/en/stable/exceptions/

    p = Path(f"{text_name}.txt")
    lines = []
    while True:
        n = len(lines)
        line = {}  # TODO construct Line object
        try:
            s = click.prompt(f"line {n}", type=str)
            click.echo(f"got input: {s}\n")
            lines.append(s)
        except KeyboardInterrupt:
            click.echo()
            continue
    