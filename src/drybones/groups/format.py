import click
from pathlib import Path

from drybones.LineDesignation import LineDesignation
from drybones.TextUtil import get_lines_and_residues_from_text_name
from drybones.PrintingUtil import print_lines_in_pager, print_lines_in_terminal, get_print_strings_of_line_for_example_formatting
from drybones.ProjectUtil import get_corpus_dir
from drybones.StringValidation import validate_string
from drybones.TextUtil import get_text_names_in_dir, select_lines_from_text_by_names, validate_text_name, get_all_texts_in_dir
from drybones.Validation import Validated, Invalidated


@click.command(no_args_is_help=True)
@click.argument("text_name", type=str)
@click.argument("line_name", required=True, type=str)
@click.pass_context
def format(ctx, text_name: str, line_name: str):
    """Print line for example formatting in grammar document."""

    # TODO figure out how to reduce this boilerplate that's getting repeated in various commands (opening the corpus and verifying the text)
    corpus_dir = get_corpus_dir(Path.cwd())
    text_name_validation = validate_text_name(text_name, corpus_dir, name_to_text=None)
    if text_name_validation is None or type(text_name_validation) is Invalidated:
        return
    text_name = text_name_validation.match

    line, = select_lines_from_text_by_names(text_name, [line_name], corpus_dir, name_to_text=None)
    ss = get_print_strings_of_line_for_example_formatting(line)
    click.echo("\n" + "\n".join(ss) + "\n")
