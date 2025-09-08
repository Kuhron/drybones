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
    d = get_char_to_alternatives_dict()
    click.echo("Accented characters and sequences that are treated as equivalent:")
    for k, base, alternatives in d.items():
        alts_str = " , ".join(alternatives)
        click.echo(f"{k} (base: {base}) <- {alts_str}")
    click.echo()
accent.add_command(accent_table)


@click.command(name="convert-string")
@click.argument("input_str", type=str, required=False, default=None)
def accent_convert_string(input_str: str|None):
    d = get_char_to_alternatives_dict()
    try:
        while True:
            s = input("string> ")
            s2 = translate_diacritic_alternatives_in_string(s, d)
            click.echo(s2 + "\n")
    except KeyboardInterrupt:
        click.echo("\nQuitting string conversion.")
accent.add_command(accent_convert_string)


@click.command(name="convert-file")
@click.argument("input_fp", type=Path, required=True)
def accent_convert_file(input_fp: Path):
    d = get_char_to_alternatives_dict()
    with open(input_fp) as f:
        contents = f.read()
    s = translate_diacritic_alternatives_in_string(contents, d)
    with open(input_fp, "w") as f:
        f.write(s)
accent.add_command(accent_convert_file)
