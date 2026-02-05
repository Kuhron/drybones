# things related to showing what's in a text without editing anything

import click
from pathlib import Path

from drybones.LineDesignation import LineDesignation
from drybones.TextUtil import get_lines_and_residues_from_text_name
from drybones.PrintingUtil import print_lines_in_pager, print_lines_in_terminal
from drybones.ProjectUtil import get_corpus_dir
from drybones.StringValidation import validate_string
from drybones.TextUtil import get_text_names_in_dir, select_lines_from_text_by_names, validate_text_name, get_all_texts_in_dir
from drybones.Validation import Validated, Invalidated


@click.command(no_args_is_help=True)
@click.argument("text_name", type=str)
@click.argument("line_name", required=False, type=str)
@click.pass_context
def read(ctx, text_name: str, line_name: str):
    """View text contents without editing."""
    # TODO figure out how to reduce this boilerplate that's getting repeated in various commands (opening the corpus and verifying the text)
    corpus_dir = get_corpus_dir(Path.cwd())
    name_to_text = get_all_texts_in_dir(corpus_dir, with_contents=True)
    text_name_validation = validate_text_name(text_name, corpus_dir, name_to_text=name_to_text)
    if text_name_validation is None or type(text_name_validation) is Invalidated:
        return
    text_name = text_name_validation.match
    # click.echo(f"Reading text {text_name}", err=True)

    if line_name is None:
        # read the whole text, leave line numbers as None
        line_names_to_read = None
    else:
        line_names_to_read = [line_name]

    lines_to_read = select_lines_from_text_by_names(text_name, line_names_to_read, corpus_dir, name_to_text=name_to_text)
    if len(lines_to_read) > 1:
        print_lines_in_pager(lines_to_read)
    else:
        print_lines_in_terminal(lines_to_read)
