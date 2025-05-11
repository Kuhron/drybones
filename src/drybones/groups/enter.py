# things related to raw data entry of texts via the command line
# start simple and add functionality later, don't kitchen-sink one subcommand


import click
from pathlib import Path

from drybones.Cell import Cell
from drybones.Line import Line
from drybones.Row import Row
from drybones.RowLabel import RowLabel, DEFAULT_ALIGNED_ROW_LABELS, DEFAULT_LINE_NUMBER_LABEL


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

    while True:
        line_number = len(lines) + 1
        line_number_cell = Cell([str(line_number)])
        line_number_row = Row(DEFAULT_LINE_NUMBER_LABEL, cells=[line_number_cell])

        rows = [line_number_row]
        click.echo(f"Ln:\t{text_name} {line_number}")
        label_index = 0
        while True:
            label = DEFAULT_ALIGNED_ROW_LABELS[label_index]
            try:
                s = click.prompt(label, type=str, default="")
                
                # TODO integrate with logic from repl.py for command inputs
                if s == ":q":
                    return

                cell = Cell(strs=[s])
                row = Row(label, cells=[cell])  # let the cells just be whatever the user input for now, don't enforce parsing/length/etc. yet
                rows.append(row)
                label_index += 1
                if label_index >= len(DEFAULT_ALIGNED_ROW_LABELS):
                    break
            except click.Abort:
                click.echo()
                continue
                # keep label_index the same so user can try again
        line = Line(line_number, rows)
        lines.append(line)
        with p.open(mode="a") as f:
            f.write(Line.BEFORE_LINE)
            for row in line.rows:
                f.write(row.to_str(with_label=True) + "\n")
            f.write(Line.AFTER_LINE)
