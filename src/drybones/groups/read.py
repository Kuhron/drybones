# things related to showing what's in a text without editing anything

import click
from pathlib import Path

from drybones.ReadingUtil import get_text_names_in_dir, get_lines_and_residues_from_text_name
from drybones.PrintingUtil import print_lines_in_pager, print_lines_in_terminal
from drybones.ProjectUtil import get_corpus_dir
from drybones.StringValidation import validate_string
from drybones.Validation import Validated, Invalidated


@click.command
@click.argument("text_name")
@click.argument("line_number", required=False, type=int)
@click.pass_context
def read(ctx, text_name: str, line_number: int):
    """View text contents without editing."""
    corpus_dir = get_corpus_dir(Path.cwd())
    text_name_validation = validate_text_name(text_name, corpus_dir)
    if text_name_validation is None or type(text_name_validation) is Invalidated:
        return
    text_name = text_name_validation.match
    click.echo(f"Reading text {text_name}", err=True)

    lines = get_lines_and_residues_from_text_name(text_name, corpus_dir).lines  # should make a cache so it's not re-parsing the whole text file every time user runs a command

    line_numbers_to_read = None
    if line_number is None:
        # read the whole text, leave line numbers as None
        pass
    else:
        if type(validate_line_number(line_number, lines, text_name)) is Invalidated:
            return
        line_numbers_to_read = [line_number]
    
    if line_numbers_to_read is not None:
        lines = [lines[i-1] for i in line_numbers_to_read]
    if len(lines) > 1:
        print_lines_in_pager(lines)
    else:
        print_lines_in_terminal(lines)


def validate_text_name(text_name: str, corpus_dir: Path):
    text_name_options = get_text_names_in_dir(corpus_dir)
    validation = validate_string(text_name, text_name_options)
    if validation is None:
        return None
    elif type(validation) is Invalidated:
        if len(validation.options) > 0:
            s2 = "Did you mean one of these?\n  " + "\n  ".join(validation.options)
        else:
            s2 = "There are no texts in this project yet."
        click.echo(f"Text name {text_name!r} not recognized. " + s2, err=True)
    return validation


def validate_line_number(line_number, lines, text_name):
    try:
        line_number = int(line_number)
    except (TypeError, ValueError):
        click.echo(f"Line number should be an integer, but got {line_number!r}.", err=True)
        return Invalidated()

    if line_number < 1:
        click.echo(f"Line number must be a positive integer, got {line_number}.", err=True)
        return Invalidated()

    # check if the text has this many lines
    try:
        lines[line_number-1]
    except IndexError:
        click.echo(f"Cannot access line {line_number} of text '{text_name}' because it only has {len(lines)} lines.", err=True)
        return Invalidated()
    return Validated()


