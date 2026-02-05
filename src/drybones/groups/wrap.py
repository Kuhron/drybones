# things related to placing text into the DryBones line format, with the delimiters before and after it


import click
from pathlib import Path
from typing import List

from drybones.AudacityLabelsUtil import get_audacity_labels_from_file
from drybones.Cell import Cell
from drybones.Constants import DRYBONES_FILE_EXTENSION
from drybones.FileEditingUtil import guard_against_overwriting_existing_file
from drybones.InputUtil import multiline_input
from drybones.Line import Line
from drybones.LineDesignation import LineDesignation
from drybones.Row import Row
from drybones.RowLabel import RowLabel, DEFAULT_BASELINE_RAW_LABEL, DEFAULT_START_TIME_SECONDS_LABEL, DEFAULT_END_TIME_SECONDS_LABEL
from drybones.Text import TEXT_NAME_PLACEHOLDER



@click.group(no_args_is_help=True)
def wrap():
    """Wrap strings in DryBones line delimiters."""
    pass


@click.command(name="input")
def wrap_input():
    click.echo("Type or paste your string at the prompt below.")
    s = multiline_input("> ")
    label = get_row_label_from_user()
    input_strs = s.split("\n")
    separate_lines = find_out_if_should_separate_lines(input_strs)
    lines = get_lines_from_input_strs(input_strs, input_row_label=label, separate_lines=separate_lines)

    click.echo("\nPrinting formatted line strings:")
    click.echo(get_display_str_of_lines(lines))
wrap.add_command(wrap_input)


@click.command(name="file")
@click.argument("input_fp", required=True, type=Path)
@click.argument("output_fp", required=True, type=Path)
def wrap_file(input_fp: Path, output_fp: Path):
    with open(input_fp) as f:
        input_strs = f.readlines()
    input_strs = [x[:-1] if x.endswith("\n") else x for x in input_strs]
    label = get_row_label_from_user()
    separate_lines = find_out_if_should_separate_lines(input_strs)
    lines = get_lines_from_input_strs(input_strs, input_row_label=label, separate_lines=separate_lines)
    s = get_display_str_of_lines(lines)
    with open(output_fp, "w") as f:
        f.write(s)
    click.echo(f"\nOutput written to {output_fp}")
wrap.add_command(wrap_file)


@click.command(name="audacity-labels")
@click.argument("input_fp", required=True, type=Path)
@click.argument("text_name", required=True, type=str)
def wrap_audacity_labels(input_fp: Path, text_name: str):
    output_fp = input_fp.parent / f"{text_name}{DRYBONES_FILE_EXTENSION}"
    guard_against_overwriting_existing_file(output_fp)
    try:
        aud_labels = get_audacity_labels_from_file(input_fp)
    except ValueError:
        click.echo(f"problem reading Audacity labels file", err=True)
        raise click.Abort()
    lines = []
    for i, aud_label in enumerate(aud_labels):
        designation = LineDesignation(text_name=text_name, line_name=str(i+1))
        rows = [
            Row(label=DEFAULT_BASELINE_RAW_LABEL, cells=[Cell(strs=[aud_label.text])]),
            Row(label=DEFAULT_START_TIME_SECONDS_LABEL, cells=[Cell(strs=[str(aud_label.start_time_s)])]),
            Row(label=DEFAULT_END_TIME_SECONDS_LABEL, cells=[Cell(strs=[str(aud_label.end_time_s)])]),
        ]
        line = Line(designation=designation, rows=rows)
        lines.append(line)
    s = get_display_str_of_lines(lines)
    with open(output_fp, "w") as f:
        f.write(s)
    click.echo(f"\nOutput written to {output_fp}")
wrap.add_command(wrap_audacity_labels)


def find_out_if_should_separate_lines(input_strs):
    if len(input_strs) > 1:
        separate_lines = click.confirm("\nYour input has multiple lines. Would you like to put these on separate lines? (if not, they will be multiple rows with the same label within a single line)")
    else:
        separate_lines = False
    return separate_lines


def get_lines_from_input_strs(input_strs: List[str], input_row_label: RowLabel, separate_lines: bool) -> List[Line]:
    text_name = TEXT_NAME_PLACEHOLDER
    if separate_lines:
        row_texts_grouped = [[x] for x in input_strs]
    else:
        row_texts_grouped = [[x for x in input_strs]]
    lines = []
    for i, group in enumerate(row_texts_grouped):
        rows = []
        for row_text in group:
            cell = Cell([row_text])
            row = Row(label=input_row_label, cells=[cell])
            rows.append(row)
        line = Line(designation=LineDesignation(text_name=text_name, line_name=str(i+1)), rows=rows)
        lines.append(line)
    return lines


def get_display_str_of_lines(lines: List[Line]):
    strs = []
    for line in lines:
        strs.append(line.to_string_for_drybones_file())
    return "\n".join(strs)


def get_row_label_from_user() -> RowLabel:
    click.echo("\n\nEnter the row label that you want for this data.")
    label_str = input("> ")
    label = RowLabel(label_str, aligned=False)
    return label
