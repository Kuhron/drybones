# things related to showing what's in a text without editing anything

import click
from pathlib import Path

from drybones.ReadingUtil import get_text_names_in_dir, get_lines_and_residues_from_text_name, validate_text_name, validate_line_number
from drybones.PrintingUtil import print_lines_in_pager, print_lines_in_terminal
from drybones.ProjectUtil import get_corpus_dir
from drybones.StringValidation import validate_string
from drybones.Validation import Validated, Invalidated


@click.command(no_args_is_help=True)
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
        # FIXME it should be by designation, not index
        raise NotImplementedError("fixme")
        lines = [lines[i-1] for i in line_numbers_to_read]
    if len(lines) > 1:
        print_lines_in_pager(lines)
    else:
        print_lines_in_terminal(lines)

