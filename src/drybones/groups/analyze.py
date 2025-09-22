# things relating to a word analysis (a parse/gloss of a wordform)

import click
from collections import Counter
from pathlib import Path
from typing import List

from drybones.AnalysisUtil import get_known_analyses, convert_counter_to_list
from drybones.BasicREPL import BasicREPL
from drybones.DiacriticsUtil import get_char_to_alternatives_dict, translate_diacritic_alternatives_in_string
from drybones.InvalidInput import InvalidInput
from drybones.ProjectUtil import get_corpus_dir
from drybones.ReadingUtil import get_lines_from_all_drybones_files_in_dir
from drybones.REPLUtil import unpack_args, validate_int
from drybones.WordAnalysis import WordAnalysis


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
                if last_seen_analyses is None:
                    click.echo("Cannot process a command if no analyses have been found yet. Please search for a wordform first.")
                    continue
                command, *args = directive
                if command == "reassign":
                    command_result = process_reassign_directive(analyses=last_seen_analyses, args=args)
                elif command == "reanalyze":
                    command_result = process_reanalyze_directive(analyses=last_seen_analyses, args=args)
                elif command == "view":
                    command_result = process_view_directive(analyses=last_seen_analyses, args=args)
                else:
                    click.echo(f"unknown command: {command!r}", err=True)
                    continue

                if command_result is InvalidInput:
                    # whoever returned this should print why it is invalid, so user can understand
                    continue
            elif form is not None:
                if not match_diacritics:
                    form = translate_diacritic_alternatives_in_string(form, diacritics_dict, to_base=True)
                print(f"{form = }")
                analyses = known_analyses_by_word.get(form, Counter())
                analyses = convert_counter_to_list(analyses)
                analyses = sorted(analyses, key=lambda a: (a.get_parse_str(), a.get_gloss_str()))
                last_seen_analyses = analyses

                if len(analyses) == 0:
                    click.echo(f"form {form!r} has no known analyses")
                    continue

                click.echo(f"known analyses for form {form!r}:")
                for i, a in enumerate(analyses):
                    click.echo(f"{i+1}. {a.str}")
            else:
                raise Exception("form or directive must be non-None")  # raise rather than echo because this would be an actual bug, not just invalid input


def process_reassign_directive(analyses, args):
    # take all places where one analysis is used, and replace it with another analysis
    # TODO when reassigning analysis, make sure you don't change the baseline form!
    arg_names = ("from_number", "to_number")
    args = unpack_args(args, arg_names)
    if args is InvalidInput:
        return InvalidInput
    from_number = validate_int(args.from_number, min_value=1, max_value=len(analyses))
    to_number = validate_int(args.to_number, min_value=1, max_value=len(analyses))
    if from_number is InvalidInput or to_number is InvalidInput:
        return InvalidInput

    from_index, to_index = from_number - 1, to_number - 1
    print(f"going to reassign analysis index {from_index} to {to_index}")
    print("not implemented")


def process_reanalyze_directive(analyses, args):
    # take all places where one analysis is used, and create a new analysis to replace it
    print("not implemented")


def process_view_directive(analyses: List[WordAnalysis], args):
    # view examples that use this analysis
    arg_names = ("number",)
    args = unpack_args(args, arg_names)
    if args is InvalidInput:
        return InvalidInput
    number = validate_int(args.number, min_value=1, max_value=len(analyses))
    if number is InvalidInput:
        return InvalidInput
    index = number - 1
    analysis_to_view = analyses[index]
    click.echo(f"Viewing analysis:\n{analysis_to_view}\n")
    # TODO show list of examples using this analysis
    print("not implemented")
