import sys, tempfile, os
from subprocess import call
from pathlib import Path
import click

from drybones.ProjectUtil import get_corpus_dir
from drybones.TextUtil import validate_text_name
from drybones.StringValidation import validate_string
from drybones.TextUtil import get_drybones_file_from_text_name, get_all_texts_in_dir
from drybones.Validation import Validated, Invalidated


EDITOR = os.environ.get("EDITOR", "vim")  # https://stackoverflow.com/a/6309753/7376935


@click.command(no_args_is_help=True)
@click.argument("text_name")
@click.pass_context
def edit(ctx, text_name: str):
    """Edit the .dry file for a text."""
    corpus_dir = get_corpus_dir(Path.cwd())
    name_to_text = get_all_texts_in_dir(corpus_dir, with_contents=False)
    text_name_validation = validate_text_name(text_name, corpus_dir, name_to_text=name_to_text)
    if text_name_validation is None or type(text_name_validation) is Invalidated:
        return
    text_name = text_name_validation.match
    click.echo(f"Editing text {text_name}", err=True)
    fp = get_drybones_file_from_text_name(text_name, corpus_dir, name_to_text=name_to_text)
    open_file_in_editor(fp)


def get_message_typed_in_temp_file():
    initial_message = b""

    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(initial_message)
        tf.flush()
        call([EDITOR, tf.name])

        # do the parsing with `tf` using regular File operations.
        # for instance:
        tf.seek(0)

        with open(tf.name) as f:
            edited_message = f.read()
    
    return edited_message


def open_file_in_editor(fp: Path):
    click.edit(filename=str(fp))
