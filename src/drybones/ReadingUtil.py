# helper functions for getting contents of texts for display to user
# but NOT for actually doing any displaying

import click
from collections import defaultdict
from pathlib import Path
from typing import List

from drybones.Cell import Cell
from drybones.Constants import DRYBONES_FILE_EXTENSION
from drybones.Line import Line
from drybones.LinesAndResidues import LinesAndResidues
from drybones.Row import Row
from drybones.RowLabel import RowLabel, DEFAULT_LINE_DESIGNATION_LABEL, DEFAULT_ROW_LABELS_BY_STRING
from drybones.Text import Text


def get_drybones_file_from_text_name(text_name: str, corpus_dir: Path) -> Path:
    name_to_text = get_all_texts_in_dir(corpus_dir, with_contents=False)
    return name_to_text[text_name].source_fp


def get_lines_and_residues_from_text_name(text_name: str, corpus_dir: Path) -> LinesAndResidues:
    fp = get_drybones_file_from_text_name(text_name, corpus_dir)
    return get_lines_and_residues_from_drybones_file(fp)


def get_raw_line_strs_from_file(fp: Path, with_newlines:bool=False) -> List[str]:
    with open(fp) as f:
        lines = f.readlines()
    for l in lines:
        assert l[-1] == "\n"
    if with_newlines:
        return lines
    else:
        return [l[:-1] for l in lines]


def get_lines_and_residues_from_drybones_file(fp: Path, enforce_unique_designations:bool=True) -> LinesAndResidues:
    line_groups, residues_by_location = get_line_group_strings_from_drybones_file(fp)
    lines = []
    row_labels_by_string = {k:v for k,v in DEFAULT_ROW_LABELS_BY_STRING.items()}
    if enforce_unique_designations:
        desigs_seen = set()
    for line_group in line_groups:
        line_designation = None
        row_strs = line_group.split("\n")
        rows = []
        row_length = None
        for row_str in row_strs:
            if row_str == "":
                continue
            label_str, *row_text_pieces = row_str.split(RowLabel.AFTER_LABEL_CHAR)
            if len(row_text_pieces) == 0:
                click.echo(f"\nError! in file {fp}\nrow has no label:\n{row_str!r}\n", err=True)
                raise click.Abort()
            else:
                row_text = RowLabel.AFTER_LABEL_CHAR.join(row_text_pieces)
            
            row_text = row_text.strip()
            try:
                label = row_labels_by_string[label_str]
            except KeyError:
                label = RowLabel(label_str, aligned=False)
                row_labels_by_string[label_str] = label

            if label == DEFAULT_LINE_DESIGNATION_LABEL:
                line_designation = row_text

            if label.is_aligned():
                cell_texts = row_text.split(Row.INTRA_ROW_DELIMITER)
                cells = []
                for cell_text in cell_texts:
                    cell = Cell(cell_text.split(Cell.INTRA_CELL_DELIMITER))
                    cells.append(cell)
                this_row_length = len(cells)
                if row_length is None:
                    row_length = this_row_length
                else:
                    if this_row_length != row_length:
                        line_group_display = "\n> " + line_group.replace("\n", "\n> ") + "\n"
                        click.echo(f"\nError! in file {fp}\nIn line group:\n{line_group_display}\nexpected row of length {row_length} but got {this_row_length}:\n{row_text}", err=True)
                        raise click.Abort()
            else:
                cells = [Cell([row_text])]
            
            row = Row(label, cells)
            rows.append(row)
        if enforce_unique_designations:
            if line_designation in desigs_seen:
                click.echo(f"duplicate line designation: {line_designation!r}", err=True)
                raise click.Abort()
            else:
                desigs_seen.add(line_designation)
        line = Line(line_designation, rows)
        lines.append(line)
    # click.echo(f"loaded lines from {fp}")
    return LinesAndResidues(lines, residues_by_location)


def get_line_group_strings_from_drybones_file(fp: Path):
    with open(fp) as f:
        contents = f.read()
    l = contents.split(Line.BEFORE_LINE)
    groups = []
    residue_before_first_group = l[0]
    residues_by_location = {-0.5: residue_before_first_group}  # location is +/- 0.5 from group index (regardless of the group's labeled number/designation)
    for s in l[1:]:
        group, *residues = s.split(Line.AFTER_LINE)  # there may be stray AFTER_LINE delimiters in the residue
        groups.append(group)
        if len(residues) > 0:
            residue = Line.AFTER_LINE.join(residues)
            last_group_index = len(groups) - 1
            location = last_group_index + 0.5
            assert location not in residues_by_location
            residues_by_location[location] = residue
    # TODO make a LineGroupString object and ResidueString object for holding the original file contents after breaking it apart
    # then can call a function on a LineGroupString to parse it into a Line
    # but want the top-level parse command call to be able to just grab the original string for a group that was unedited, and for a residue, without me stripping off whitespace and then adding it back on (error prone)
    return groups, residues_by_location


def get_text_from_file(fp: Path, with_contents: bool=True):
    name = fp.stem  # for now just take name from the filename, but later want it to match the line designations and/or be in some metadata in the text's .dry file itself
    if with_contents:
        lines, residues = get_lines_and_residues_from_drybones_file(fp)
    else:
        lines, residues = [], []
    t = Text(name, lines, residues, source_fp=fp)
    return t


def get_text_names_in_dir(d: Path):
    name_to_text = get_all_texts_in_dir(d, with_contents=False)
    return list(name_to_text.keys())


def get_all_texts_in_dir(d: Path, with_contents: bool=True):
    fps = get_all_drybones_files_in_dir(d)
    name_to_text = {}
    name_to_fps = defaultdict(list)
    has_duplicates = False
    for fp in fps:
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

    if has_duplicates:
        click.echo("\nDuplicate text names found:")
        for name, these_fps in sorted(name_to_fps.items()):
            if len(these_fps) > 1:
                click.echo(f"\tText name {name!r}:")
                for fp in sorted(these_fps):
                    click.echo(f"\t\t{fp}")
        raise click.Abort()
    
    return name_to_text


def get_all_drybones_files_in_dir(d: Path):
    return list(d.glob("**/*" + DRYBONES_FILE_EXTENSION))


def get_lines_from_all_drybones_files_in_dir(d: Path):
    name_to_text = get_all_texts_in_dir(d)
    lines = []
    for i, (name, t) in enumerate(name_to_text.items()):
        lines += t.lines
        click.echo(f"loading lines from file {i+1}/{len(name_to_text)}\r", nl=False)
    click.echo()
    return lines
