# things related to showing what's in a text without editing anything

import click
from pathlib import Path

from drybones.LineDesignation import LineDesignation
from drybones.LineUtil import get_line_designation_to_line_dict_from_list
from drybones.ReadingUtil import get_text_names_in_dir, get_lines_and_residues_from_text_name, validate_text_name
from drybones.PrintingUtil import print_lines_in_pager, print_lines_in_terminal
from drybones.ProjectUtil import get_corpus_dir
from drybones.StringValidation import validate_string
from drybones.Validation import Validated, Invalidated


@click.command(no_args_is_help=True)
@click.argument("text_name", type=str)
@click.argument("line_name", required=False, type=str)
@click.pass_context
def read(ctx, text_name: str, line_name: str):
    """View text contents without editing."""
    corpus_dir = get_corpus_dir(Path.cwd())
    text_name_validation = validate_text_name(text_name, corpus_dir)
    if text_name_validation is None or type(text_name_validation) is Invalidated:
        return
    text_name = text_name_validation.match
    # click.echo(f"Reading text {text_name}", err=True)

    lines = get_lines_and_residues_from_text_name(text_name, corpus_dir).lines  # should make a cache so it's not re-parsing the whole text file every time user runs a command
    designation_to_line = get_line_designation_to_line_dict_from_list(lines)

    text_name_for_line_designations ,= set(x.text_name for x in designation_to_line.keys())
    if line_name is None:
        # read the whole text, leave line numbers as None
        lines_to_read = lines
    else:
        line_names_to_read = [line_name]
        line_designations_to_read = [LineDesignation(text_name_for_line_designations, x) for x in line_names_to_read]
        lines_to_read = [designation_to_line[x] for x in line_designations_to_read]

    if len(lines_to_read) > 1:
        print_lines_in_pager(lines_to_read)
    else:
        print_lines_in_terminal(lines_to_read)
