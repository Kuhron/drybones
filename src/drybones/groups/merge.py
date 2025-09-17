import click
from pathlib import Path

from drybones.FileEditingUtil import setup_file_editing_operation, finish_file_editing_operation
from drybones.Line import Line
from drybones.Row import Row
from drybones.RowLabel import RowLabel


@click.command(no_args_is_help=True)
@click.argument("input_fp1", required=True, type=Path)
@click.argument("rows1", required=True, type=str)
@click.argument("input_fp2", required=True, type=Path)
@click.argument("rows2", required=True, type=str)
@click.argument("output_fp", required=True, type=Path)
@click.pass_context
def merge(ctx, input_fp1, rows1, input_fp2, rows2, output_fp):
    """Merge lines from two files, specifying which rows should come from which file.

    # can remap row labels as they are taken from a file, e.g. "Baseline>BaselineRaw" means to get "Baseline" from the file but output it instead with the label "BaselineRaw"\n
    # '*' means get all other row labels from this file (the string '*' itself should be a prohibited label)\n
    # '/' separating outputs means the input row will be copied to multiple rows in the output\n

    # mockup\n
    $ dry merge Hevi_Raw.dry "Baseline > BaselineRaw" Hevi.dry "Parse, Gloss, Translation" Hevi_combined.dry\n
    $ dry merge HkNb4.dry "Baseline, Translation" HkNb4_Raw.dry "*" Hevi_combined.dry\n
    $ dry merge Hevi_Raw.dry "Baseline > BaselineRaw / BaselineToClean, Translation > TranslationRaw / TranslationToClean" Hevi.dry "*" Hevi_combined.dry\n
    $ dry merge WP2.dry "BaselineRaw>Baseline,TranslationRaw>Translation" WP2.dry "BaselineRaw,TranslationRaw" a.dry\n
    """

    assert output_fp not in [input_fp1, input_fp2], "output file must be different from input files"
    if output_fp.exists():
        raise FileExistsError(output_fp)

    _new_drybones_fp1, lines1, residues_by_location1, line_designations_in_order1, lines_by_designation1, _initial_hash1 = setup_file_editing_operation(input_fp1, overwrite=False)
    _new_drybones_fp2, lines2, residues_by_location2, line_designations_in_order2, lines_by_designation2, _initial_hash2 = setup_file_editing_operation(input_fp2, overwrite=False)
    # we won't use the hashes to guard against overwriting because this operation makes a new file

    all_labels1 = get_all_row_labels(lines1, exclude_designation=True)
    all_labels2 = get_all_row_labels(lines2, exclude_designation=True)

    if line_designations_in_order1 != line_designations_in_order2:
        raise ValueError("line designations must match exactly, in the same order")
    line_designations_in_order = line_designations_in_order1

    directives = parse_row_directives(input_fp1, rows1, all_labels1, input_fp2, rows2, all_labels2)
    new_lines_by_designation = {}

    fp_to_index = {input_fp1: 0, input_fp2: 1}
    
    for desig in line_designations_in_order:
        line1 = lines_by_designation1[desig]
        line2 = lines_by_designation2[desig]
        lines_for_getting_rows = [line1, line2]
        rows = []
        for fp, from_label_str, to_label_str in directives:
            fp_index = fp_to_index[fp]
            line_to_get_row_from = lines_for_getting_rows[fp_index]
            try:
                from_label = line_to_get_row_from.row_label_by_string[from_label_str]
            except KeyError:
                # this row label not in this line from the file where we want to take this row label from
                continue
            from_row = line_to_get_row_from[from_label]
            to_label = from_label.relabel(to_label_str)
            new_row = from_row.relabel(to_label)
            rows.append(new_row)
        new_line = Line(desig, rows)
        new_lines_by_designation[desig] = new_line
    
    residues_by_location_chosen = {}  # default value if no directive gets the residues
    for fp, from_label_str, to_label_str in directives:
        if from_label_str == RowLabel.RESIDUES_PSEUDO_LABEL:
            residues_by_location_chosen = [residues_by_location1, residues_by_location2][fp_to_index[fp]]
            break

    # FIXME now the lines have duplicate designations because it thinks the designation in a file's line strings is a content line

    finish_file_editing_operation(new_drybones_fp=output_fp, residues_by_location=residues_by_location_chosen, line_designations_in_order=line_designations_in_order, new_lines_by_designation=new_lines_by_designation, initial_hash=None)
    click.echo("done merging")


def get_all_row_labels(lines, exclude_designation=True):
    res = set()
    for line in lines:
        res |= line.get_all_row_labels(string=True, exclude_designation=exclude_designation)
    return res


def parse_row_directives(fp1, s1, all_labels1, fp2, s2, all_labels2):
    # have a "row label" for which file's residues to keep, do not allow mixing of residues from multiple files
    residue_label = RowLabel.RESIDUES_PSEUDO_LABEL
    all_other_rows_label = RowLabel.ALL_OTHER_ROWS_CHAR

    residue_explicitly_mentioned = False
    all_other_rows_mentioned = False
    fp_for_all_other_rows = None
    all_labels_for_all_other_rows = set()
    # from_labels_seen_for_all_other_rows = set()

    row_labels1 = [x.strip() for x in s1.split(",")]
    row_labels2 = [x.strip() for x in s2.split(",")]

    directives = []
    from_labels_seen1 = set()
    from_labels_seen2 = set()
    to_labels_to_exclude_from_all_other_labels = set()
    for fp_index, fp, row_labels, all_labels in zip([1, 2], [fp1, fp2], [row_labels1, row_labels2], [all_labels1, all_labels2]):
        from_labels_seen = from_labels_seen1 if fp_index == 1 else from_labels_seen2  # if fp_index == 2
        for row_label in row_labels:
            try:
                from_label, to_labels_str = row_label.split(">")
                to_labels = to_labels_str.strip().split(RowLabel.MULTIPLE_ROWS_SEPARATOR_CHAR)
                has_mapping = True
            except ValueError:
                from_label = row_label
                to_labels = [row_label]
                has_mapping = False
            
            if row_label != RowLabel.ALL_OTHER_ROWS_CHAR:
                from_labels_seen.add(from_label)
            
            # error if residue or * is mapped from or to
            if has_mapping:
                labels_involved = [from_label] + to_labels
                if residue_label in labels_involved or all_other_rows_label in labels_involved:
                    click.echo(f"cannot map to/from {residue_label!r} or {all_other_rows_label!r}", err=True)
                    raise click.Abort()
            else:
                assert len(to_labels) == 1, "can't have multiple output labels if there is no mapping"

            from_label = from_label.strip()
            if from_label == residue_label:
                residue_explicitly_mentioned = True
            elif from_label == all_other_rows_label:
                all_other_rows_mentioned = True
                fp_for_all_other_rows = fp
                all_labels_for_all_other_rows = all_labels
                # from_labels_seen_for_all_other_rows = from_labels_seen
                to_labels = []  # don't add "* -> *" as a mapping

            to_labels = [x.strip() for x in to_labels]
            for to_label in to_labels:
                tup = (fp, from_label, to_label)
                directives.append(tup)
                to_labels_to_exclude_from_all_other_labels.add(to_label)

    if all_other_rows_mentioned:
        # '*' refers to all labels found in the file which are not mapped TO

        # all_other_labels_to_use = all_labels_for_all_other_rows - from_labels_seen_for_all_other_rows
        all_other_labels_to_use = all_labels_for_all_other_rows - to_labels_to_exclude_from_all_other_labels
        for label in all_other_labels_to_use:
            tup = (fp_for_all_other_rows, label, label)
            directives.append(tup)

        # include residue in * if it is not explicitly mentioned
        if not residue_explicitly_mentioned:
            new_tup = (fp_for_all_other_rows, residue_label, residue_label)
            directives.append(new_tup)

    for fp, x, y in directives:
        assert type(x) is str, x
        assert type(y) is str, y

    to_labels_seen = set()
    click.echo("'dry merge' directives received:")
    for fp, from_label, to_label in directives:
        click.echo(f"{[fp1, fp2].index(fp)+1} : {from_label} -> {to_label}")
        assert to_label not in to_labels_seen, f"duplicate label mapped to: {to_label}"
        from_labels_seen = from_labels_seen1 if fp == fp1 else from_labels_seen2 if fp == fp2 else None
        if from_label != RowLabel.ALL_OTHER_ROWS_CHAR:
            from_labels_seen.add(from_label)  # do this after we've computed all_other_labels_to_use, so then we can see which labels were actually omitted from a file
        to_labels_seen.add(to_label)
        if from_label == RowLabel.RESIDUES_PSEUDO_LABEL:
            assert to_label == RowLabel.RESIDUES_PSEUDO_LABEL, "residues cannot be mapped from"
        else:
            assert to_label not in RowLabel.PROHIBITED_STRINGS, f"row label string {to_label!r} not allowed"
    click.echo()

    for fp, all_labels, from_labels_seen in zip([fp1, fp2], [all_labels1, all_labels2], [from_labels_seen1, from_labels_seen2]):
        print(f"{from_labels_seen = }")
        labels_dropped = all_labels - from_labels_seen
        if len(labels_dropped) > 0:
            delim = "\n\t"
            click.echo(f"These labels were not used from file {fp}:\n\t{delim.join(sorted(str(x) for x in labels_dropped))}\n")
        else:
            click.echo(f"All labels were used from file {fp}\n")

    return directives
