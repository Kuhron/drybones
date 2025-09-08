# things relating to a word analysis (a parse/gloss of a wordform)

import click
from pathlib import Path

from drybones.AnalysisUtil import get_known_analyses
from drybones.DiacriticsUtil import get_char_to_alternatives_dict, translate_diacritic_alternatives_in_string
from drybones.ProjectUtil import get_corpus_dir
from drybones.ReadingUtil import get_lines_from_all_drybones_files_in_dir


@click.command(no_args_is_help=False)
@click.argument("form", required=True, type=str)
@click.option("--match-diacritics", "-d", type=bool, is_flag=True, help="Force matching of diacritics (which are ignored by default)")
def analyze(form: str, match_diacritics: bool=False):
    """Show/add/modify analyses for a given wordform."""
    corpus_dir = get_corpus_dir(Path.cwd())
    lines_from_all_files = get_lines_from_all_drybones_files_in_dir(corpus_dir)
    known_analyses_by_word = get_known_analyses(lines_from_all_files, match_diacritics=match_diacritics)

    d = get_char_to_alternatives_dict()
    form = translate_diacritic_alternatives_in_string(form, d, to_base=True)

    click.echo(f"known analyses for form {form!r}:")
    analyses = known_analyses_by_word.get(form, [])
    analyses = sorted(analyses, key=lambda a: (a.get_parse_str(), a.get_gloss_str()))
    for i, a in enumerate(analyses):
        click.echo(f"{i+1}. {a.str}")
    