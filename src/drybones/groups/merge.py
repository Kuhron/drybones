import click
from pathlib import Path

from drybones.FileEditingUtil import setup_file_editing_operation, finish_file_editing_operation
from drybones.RowLabel import RowLabel


@click.command
@click.argument("input_fp_1", required=True, type=Path)
@click.argument("rows_1", required=True, type=str)
@click.argument("input_fp_2", required=True, type=Path)
@click.argument("rows_2", required=True, type=str)
@click.argument("output_fp", required=True, type=Path)
@click.pass_context
def merge(ctx, input_fp_1, rows_1, input_fp_2, rows_2, output_fp):
    """Merge lines from two files, specifying which rows should come from which file."""

    # can remap row labels as they are taken from a file, e.g. "Baseline>BaselineRaw" means to get "Baseline" from the file but output it instead with the label "BaselineRaw"
    # '*' means get all other row labels from this file (the string '*' itself should be a prohibited label)
    # '/' separating outputs means the input row will be copied to multiple rows in the output

    # mockup
    """
    $ dry merge Hevi_Raw.dry "Baseline > BaselineRaw" Hevi.dry "Parse, Gloss, Translation" Hevi_combined.dry
    $ dry merge HkNb4.dry "Baseline, Translation" HkNb4_Raw.dry "*" Hevi_combined.dry
    $ dry merge Hevi_Raw.dry "Baseline > BaselineRaw / BaselineToClean, Translation > TranslationRaw / TranslationToClean" Hevi.dry "*" Hevi.combined.dry
    """

    _new_drybones_fp1, lines1, residues_by_location1, line_designations_in_order1, new_lines_by_designation1 = setup_file_editing_operation(input_fp_1, overwrite=False)
    _new_drybones_fp2, lines2, residues_by_location2, line_designations_in_order2, new_lines_by_designation2 = setup_file_editing_operation(input_fp_2, overwrite=False)

    if line_designations_in_order1 != line_designations_in_order2:
        raise ValueError("line designations must match exactly, in the same order")

    # include residue in * if it is not explicitly mentioned

    # TODO have a "row label" for which file's residues to keep, do not allow mixing of residues from multiple files
    residue_label = RowLabel.RESIDUES_PSEUDO_LABEL
    # TODO error if residue or * is mapped from or to

    # output it to the file
    raise NotImplementedError
