# command to deal with accent marks / diacritics

import click
from pathlib import Path

from drybones.DiacriticsUtil import get_char_to_alternatives_dict, translate_diacritic_alternatives_in_string


@click.group(no_args_is_help=True)
def accent():
    """Deal with accent marks (diacritics)."""
    pass


@click.command(name="table")
def accent_table():
    diacritics_dict = get_char_to_alternatives_dict()
    click.echo("Accented characters and sequences that are treated as equivalent:")
    for k, base, alternatives in diacritics_dict.items():
        alts_str = " , ".join(alternatives)
        click.echo(f"{k} (base: {base}) <- {alts_str}")
    click.echo()
accent.add_command(accent_table)


@click.command(name="convert-string")
@click.argument("input_str", type=str, required=False, default=None)
def accent_convert_string(input_str: str|None):
    diacritics_dict = get_char_to_alternatives_dict()
    if input_str is not None:
        s = translate_diacritic_alternatives_in_string(input_str, diacritics_dict)
        click.echo(s)
    else:
        try:
            while True:
                s = input("string> ")
                s2 = translate_diacritic_alternatives_in_string(s, diacritics_dict)
                click.echo(s2 + "\n")
        except KeyboardInterrupt:
            click.echo("\nQuitting string conversion.")
accent.add_command(accent_convert_string)


@click.command(name="convert-file")
@click.argument("input_fp", type=Path, required=True)
# @click.option("--skip_raw_rows", "-r", type=bool, is_flag=True, help="If the file is a .dry file, skip any rows whose labels indicate raw data (default False).")
def accent_convert_file(input_fp: Path, skip_raw_rows:bool=False):
    diacritics_dict = get_char_to_alternatives_dict()
    with open(input_fp) as f:
        contents = f.read()
    # TODO if it's a .dry file and -r flag is passed, find the raw lines (should ideally have the RowLabel objects with a bool attr for if they are raw or not, or can just see if the label str ends with "Raw" but I like that less) and pass them through to the output unaltered
    # TODO or maybe better, could do this using `dry accent convert-text [TEXT_NAME]` so it knows it's dealing with a text's .dry file and will avoid the raw rows
    # TODO once this is implemented, go back through corpus and fix any changed BaselineRaw and TranslationRaw lines
    s = translate_diacritic_alternatives_in_string(contents, diacritics_dict)
    with open(input_fp, "w") as f:
        f.write(s)
accent.add_command(accent_convert_file)
