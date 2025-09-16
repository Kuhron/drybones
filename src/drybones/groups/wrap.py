# things related to placing text into the DryBones line format, with the delimiters before and after it


import click

from drybones.Cell import Cell
from drybones.InputUtil import multiline_input
from drybones.Line import Line
from drybones.Row import Row
from drybones.RowLabel import RowLabel



@click.group(no_args_is_help=True)
def wrap():
    """Wrap strings in DryBones line delimiters"""
    pass


@click.command(name="input")
def wrap_input():
    click.echo("Type or paste your string at the prompt below.")
    s = multiline_input("> ")
    click.echo("\n\nEnter the row label that you want for this data.")
    label_str = input("> ")
    label = RowLabel(label_str, aligned=False)
    input_lines = s.split("\n")
    if len(input_lines) > 1:
        separate_lines = click.confirm("\nYour input has multiple lines. Would you like to put these on separate lines? (if not, they will be multiple rows with the same label within a single line)")
        if separate_lines:
            row_texts_grouped = [[x] for x in input_lines]
        else:
            row_texts_grouped = [[x for x in input_lines]]
    else:
        row_texts_grouped = [[x for x in input_lines]]
    click.echo("\nPrinting formatted line strings:")
    for i, group in enumerate(row_texts_grouped):
        rows = []
        for row_text in group:
            cell = Cell([row_text])
            row = Row(label=label, cells=[cell])
            rows.append(row)
        line = Line(designation=str(i+1), rows=rows)
        click.echo(line.to_string_for_drybones_file())
wrap.add_command(wrap_input)

