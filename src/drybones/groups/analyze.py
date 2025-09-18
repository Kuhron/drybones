# things relating to a word analysis (a parse/gloss of a wordform)

import click
from pathlib import Path

from drybones.AnalysisUtil import get_known_analyses
from drybones.BasicREPL import BasicREPL
from drybones.DiacriticsUtil import get_char_to_alternatives_dict, translate_diacritic_alternatives_in_string
from drybones.InvalidInput import InvalidInput
from drybones.ProjectUtil import get_corpus_dir
from drybones.ReadingUtil import get_lines_from_all_drybones_files_in_dir


@click.command()
@click.pass_context
@click.option("--match-diacritics", "-d", type=bool, is_flag=True, help="Force matching of diacritics (ignored by default)")
def analyze(ctx, match_diacritics: bool=False):
    """Show/add/modify analyses for a given wordform."""
    corpus_dir = get_corpus_dir(Path.cwd())
    lines_from_all_files = get_lines_from_all_drybones_files_in_dir(corpus_dir)
    known_analyses_by_word = get_known_analyses(lines_from_all_files, match_diacritics=match_diacritics)

    diacritics_dict = get_char_to_alternatives_dict()
    last_seen_analyses = None

    with BasicREPL(session_type_str="analyze") as repl:
        while True:
            form, directive = repl.prompt("\nEnter a form to analyze.\n> ")
            if directive is not None:
                command, *args = directive
                if command == "reassign":
                    command_result = process_reassign_directive(analyses=last_seen_analyses, args=args)
                elif command == "reanalyze":
                    command_result = process_reanalyze_directive(analyses=last_seen_analyses, args=args)
                else:
                    click.echo(f"unknown command: {command!r}", err=True)
                    continue

                if command_result is InvalidInput:
                    # whoever returned this should print why it is invalid, so user can understand
                    continue
            else:
                if not match_diacritics:
                    form = translate_diacritic_alternatives_in_string(form, diacritics_dict, to_base=True)
                print(f"{form = }")
                analyses = known_analyses_by_word.get(form, [])
                last_seen_analyses = analyses

                if len(analyses) == 0:
                    click.echo(f"form {form!r} has no known analyses")
                    continue

                click.echo(f"known analyses for form {form!r}:")
                analyses = sorted(analyses, key=lambda a: (a.get_parse_str(), a.get_gloss_str()))
                for i, a in enumerate(analyses):
                    click.echo(f"{i+1}. {a.str}")


def process_reassign_directive(analyses, args):
    # take all places where one analysis is used, and replace it with another analysis
    # TODO when reassigning analysis, make sure you don't change the baseline form!
    try:
        from_number_str, to_number_str = args
    except ValueError:
        click.echo("args should be: from_number, to_number")
        return InvalidInput
    try:
        from_index = int(from_number_str) - 1
        to_index = int(to_number_str) - 1
    except ValueError:
        click.echo(f"should be parseable ints: {from_number_str!r}, {to_number_str!r}")
        return InvalidInput
    if from_index < 0 or to_index < 0:
        click.echo(f"should be >= 1: {from_number_str}, {to_number_str}")
        return InvalidInput
    print(f"going to reassign analysis index {from_index} to {to_index}")
    print(f"not implemented")


def process_reanalyze_directive(analyses, args):
    # take all places where one analysis is used, and create a new analysis to replace it
    print(f"not implemented")
