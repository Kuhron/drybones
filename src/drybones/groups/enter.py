# things related to raw data entry of texts via the command line
# start simple and add functionality later, don't kitchen-sink one subcommand


import click
from pathlib import Path

from drybones.RowLabel import DEFAULT_ALIGNED_ROW_LABELS


@click.command
@click.argument("text_name")
def enter(text_name):
    """Enter raw data for a text. This can also be done manually in the text files themselves."""
    click.echo(f"Now entering data for text {text_name!r}. Press Ctrl+C to cancel current command, Ctrl+D to exit.")
    # TODO figure out how to get the Ctrl+C and Ctrl+D behavior to work with Click exceptions: https://click.palletsprojects.com/en/stable/exceptions/

    p = Path(f"texts/{text_name}.txt")
    p.parent.mkdir(exist_ok=True)
    if p.exists():
        raise FileExistsError(f"would overwrite text file at {p}")
    p.touch()

    lines = []

    with p.open(mode="w") as f:
        while True:
            n = len(lines) + 1
            line = {}  # TODO construct Line object
            click.echo(f"Ln:\t{text_name} {n}")
            for label in DEFAULT_ALIGNED_ROW_LABELS:
                try:
                    s = click.prompt(label, type=str, default="")
                    lines.append(s)
                    f.write(f"{label}:\t{s}\n")
                except click.Abort:
                    click.echo()
                    continue
    