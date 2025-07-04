import click
from pathlib import Path

from drybones.FileEditingUtil import setup_file_editing_operation, finish_file_editing_operation
from drybones.RowLabel import RowLabel


@click.command
@click.argument("input_fp1", required=True, type=Path)
@click.argument("rows1", required=True, type=str)
@click.argument("input_fp2", required=True, type=Path)
@click.argument("rows2", required=True, type=str)
@click.argument("output_fp", required=True, type=Path)
@click.pass_context
def merge(ctx, input_fp1, rows1, input_fp2, rows2, output_fp):
    """Merge lines from two files, specifying which rows should come from which file."""

    # can remap row labels as they are taken from a file, e.g. "Baseline>BaselineRaw" means to get "Baseline" from the file but output it instead with the label "BaselineRaw"
    # '*' means get all other row labels from this file (the string '*' itself should be a prohibited label)
    # '/' separating outputs means the input row will be copied to multiple rows in the output

    # mockup
    """
    $ dry merge Hevi_Raw.dry "Baseline > BaselineRaw" Hevi.dry "Parse, Gloss, Translation" Hevi_combined.dry
    $ dry merge HkNb4.dry "Baseline, Translation" HkNb4_Raw.dry "*" Hevi_combined.dry
    $ dry merge Hevi_Raw.dry "Baseline > BaselineRaw / BaselineToClean, Translation > TranslationRaw / TranslationToClean" Hevi.dry "*" Hevi_combined.dry
    """

    _new_drybones_fp1, lines1, residues_by_location1, line_designations_in_order1, new_lines_by_designation1 = setup_file_editing_operation(input_fp1, overwrite=False)
    _new_drybones_fp2, lines2, residues_by_location2, line_designations_in_order2, new_lines_by_designation2 = setup_file_editing_operation(input_fp2, overwrite=False)

    all_labels1 = get_all_row_labels(lines1)
    all_labels2 = get_all_row_labels(lines2)

    print("labels1:", all_labels1)
    print("labels2:", all_labels2)

    if line_designations_in_order1 != line_designations_in_order2:
        raise ValueError("line designations must match exactly, in the same order")

    directives = parse_row_directives(input_fp1, rows1, all_labels1, input_fp2, rows2, all_labels2)
    print("directives:", directives)

    # output it to the file
    raise NotImplementedError


def get_all_row_labels(lines):
    res = set()
    for line in lines:
        res |= line.get_all_row_labels(string=True)
    return res


def parse_row_directives(fp1, s1, all_labels1, fp2, s2, all_labels2):
    # have a "row label" for which file's residues to keep, do not allow mixing of residues from multiple files
    residue_label = RowLabel.RESIDUES_PSEUDO_LABEL
    all_other_rows_label = RowLabel.ALL_OTHER_ROWS_CHAR

    residue_explicitly_mentioned = False
    all_other_rows_mentioned = False
    fp_for_all_other_rows = None
    all_labels_for_all_other_rows = None
    from_labels_seen_for_all_other_rows = None

    row_labels1 = [x.strip() for x in s1.split(",")]
    row_labels2 = [x.strip() for x in s2.split(",")]

    tups = []
    for fp_index, fp, row_labels, all_labels in zip([1, 2], [fp1, fp2], [row_labels1, row_labels2], [all_labels1, all_labels2]):
        from_labels_seen = set()
        for row_label in row_labels:
            try:
                from_label, to_labels_str = row_label.split(">")
                to_labels = to_labels_str.strip().split(RowLabel.MULTIPLE_ROWS_SEPARATOR_CHAR)
                has_mapping = True
            except ValueError:
                from_label = row_label
                to_labels = [row_label]
                has_mapping = False
            
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
                from_labels_seen_for_all_other_rows = from_labels_seen


            to_labels = [x.strip() for x in to_labels]
            for to_label in to_labels:
                tup = (fp, from_label, to_label)
                tups.append(tup)

        labels_dropped = all_labels - from_labels_seen
        if len(labels_dropped) > 0:
            delim = "\n\t"
            click.echo(f"These labels were not used from file {fp}:\n\t{delim.join(sorted(str(x) for x in labels_dropped))}\n")

    if all_other_rows_mentioned:
        all_other_labels_to_use = all_labels_for_all_other_rows - from_labels_seen_for_all_other_rows
        for label in all_other_labels_to_use:
            tup = (fp_for_all_other_rows, label, label)
            tups.append(tup)

        # include residue in * if it is not explicitly mentioned
        if not residue_explicitly_mentioned:
            new_tup = (fp_for_all_other_rows, residue_label, residue_label)
            tups.append(new_tup)

    for fp, x, y in tups:
        assert type(x) is str, x
        assert type(y) is str, y

    return tups
