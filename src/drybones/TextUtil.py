from collections import defaultdict
from typing import List, Dict
import click
from pathlib import Path
from drybones.LineDesignation import LineDesignation
from drybones.LineUtil import get_line_designation_to_line_dict_from_list
from drybones.LinesAndResidues import LinesAndResidues
from drybones.ReadingUtil import get_all_drybones_files_in_dir, get_lines_and_residues_from_drybones_file
from drybones.StringValidation import validate_string
from drybones.Text import Text
from drybones.Validation import Invalidated, Validated


def get_all_texts_in_dir(d: Path, with_contents: bool=True):
    fps = get_all_drybones_files_in_dir(d)
    name_to_text = {}
    name_to_fps = defaultdict(list)
    has_duplicates = False
    for i, fp in enumerate(fps):
        click.echo(f"loading .dry files in corpus: {i+1}/{len(fps)} files complete\r", nl=False)
        text = get_text_from_file(fp, with_contents=with_contents)
        name = text.name
        name_to_fps[name].append(fp)
        if len(name_to_fps[name]) > 1:
            has_duplicates = True

        # if we have any duplicates already, we no longer care about returning the dict of name to text
        # but we will still check for more duplicates so we can list all of them at once to the user
        if not has_duplicates:
            # add this text to the dict that we will return
            name_to_text[name] = text
    click.echo()  # after carriage return

    if has_duplicates:
        click.echo("\nDuplicate text names found:")
        for name, these_fps in sorted(name_to_fps.items()):
            if len(these_fps) > 1:
                click.echo(f"\tText name {name!r}:")
                for fp in sorted(these_fps):
                    click.echo(f"\t\t{fp}")
        raise click.Abort()

    return name_to_text



def get_drybones_file_from_text_name(text_name: str, corpus_dir: Path, key_error_returns_key: bool=False, name_to_text: Dict[str, Text] | None = None) -> Path:
    if name_to_text is None:
        name_to_text = get_all_texts_in_dir(corpus_dir, with_contents=False)
    try:
        text = name_to_text[text_name]
    except KeyError as e:
        if key_error_returns_key:
            # treat the passed "text_name" string as a filename
            return Path(text_name)
        else:
            click.echo(f"text name {text_name!r} not found", err=True)
            raise click.Abort()

    return text.source_fp


def get_original_transcript_file_from_text_name(text_name: str, corpus_dir: Path, name_to_text: Dict[str, Text] | None = None):
    if name_to_text is None:
        name_to_text = get_all_texts_in_dir(corpus_dir, with_contents=False)
    try:
        text = name_to_text[text_name]
    except KeyError:
        click.echo(f"text name {text_name!r} not found", err=True)
        raise click.Abort()
    
    dry_fp = text.source_fp
    return dry_fp.with_name(dry_fp.stem + "_OriginalTranscript.eaf")


def get_text_from_file(fp: Path, with_contents: bool=True):
    name = fp.stem  # for now just take name from the filename, but later want it to match the line designations and/or be in some metadata in the text's .dry file itself
    if with_contents:
        lines, residues = get_lines_and_residues_from_drybones_file(fp)
    else:
        lines, residues = [], []
    t = Text(name, lines, residues, source_fp=fp)
    return t


def get_text_names_in_dir(d: Path, name_to_text: Dict[str, Text] | None = None):
    if name_to_text is None:
        name_to_text = get_all_texts_in_dir(d, with_contents=False)
    return list(name_to_text.keys())


def validate_text_name(text_name: str, corpus_dir: Path, name_to_text: Dict[str, Text] | None = None) -> (Validated | Invalidated | None):
    text_name_options = get_text_names_in_dir(corpus_dir, name_to_text=name_to_text)
    validation = validate_string(text_name, text_name_options)
    if validation is None:
        return None
    elif type(validation) is Invalidated:
        if len(validation.options) > 0:
            s2 = "Did you mean one of these?\n  " + "\n  ".join(validation.options)
        else:
            s2 = "There are no texts in this project yet."
        click.echo(f"Text name {text_name!r} not recognized. " + s2, err=True)
    return validation


def get_lines_and_residues_from_text_name(text_name: str, corpus_dir: Path, name_to_text: Dict[str, Text] | None = None) -> LinesAndResidues:
    fp = get_drybones_file_from_text_name(text_name, corpus_dir, name_to_text=name_to_text)
    return get_lines_and_residues_from_drybones_file(fp)


def select_lines_from_text_by_names(text_name: str, line_names: List[str] | None, corpus_dir: Path, name_to_text: Dict[str, Text] | None = None):
    lines = get_lines_and_residues_from_text_name(text_name, corpus_dir, name_to_text=name_to_text).lines  # should make a cache so it's not re-parsing the whole text file every time user runs a command
    designation_to_line = get_line_designation_to_line_dict_from_list(lines)
    text_name_for_line_designations ,= set(x.text_name for x in designation_to_line.keys())

    if line_names is None:
        lines_to_read = lines
    else:
        line_designations_to_read = [LineDesignation(text_name_for_line_designations, x) for x in line_names]
        lines_to_read = []
        for des in line_designations_to_read:
            try:
                l = designation_to_line[des]
                lines_to_read.append(l)
            except KeyError:
                click.echo(f"line designation not found: {des!r}", err=True)
    return lines_to_read


def get_lines_from_all_drybones_files_in_dir(d: Path, name_to_text: Dict[str, Text] | None = None):
    if name_to_text is None:
        name_to_text = get_all_texts_in_dir(d, with_contents=True)
    lines = []
    for i, (name, t) in enumerate(name_to_text.items()):
        lines += t.lines
    click.echo()
    return lines
