# things related to creating/deleting/listing texts and other basic operations on them
# NOT for parsing/editing

import click
from pathlib import Path

from drybones.Constants import DRYBONES_FILE_EXTENSION
from drybones.ProjectUtil import get_corpus_dir
from drybones.ReadingUtil import get_all_texts_in_dir



@click.group(no_args_is_help=True)
def text():
    """Create and manage texts within a project."""
    pass


@click.command(name="create")
@click.argument("text_name")
def text_create(text_name):
    click.echo(f"creating text {text_name!r}")
    click.echo("text_create not implemented", err=True)
text.add_command(text_create)


@click.command(name="list")
def text_list():
    corpus_dir = get_corpus_dir(Path.cwd())
    name_to_text = get_all_texts_in_dir(corpus_dir, with_contents=False)
    click.echo("DryBones texts in the current corpus:")
    for name, t in sorted(name_to_text.items()):
        click.echo(f"Text {name!r}, source: {t.source_fp}")
    click.echo()
text.add_command(text_list)

