import click
from pathlib import Path



@click.command
@click.argument("input_fp_1", required=True, type=Path)
@click.argument("rows_1", required=True, type=str)
@click.argument("input_fp_2", required=True, type=Path)
@click.argument("rows_2", required=True, type=str)
@click.option("--output_fp", "-o", required=False, type=Path)
@click.pass_context
def merge(ctx, input_fp_1, rows_1, input_fp_2, rows_2, output_fp):
    """Merge lines from two files, specifying which rows should come from which file."""

    # can remap row labels as they are taken from a file, e.g. "Baseline:BaselineRaw" means to get "Baseline" from the file but output it instead with the label "BaselineRaw"
    # '*' means get all other row labels from this file (the string '*' itself should be a prohibited label)
    # '/' separating outputs means the input row will be copied to multiple rows in the output

    # mockup
    "dry merge Hevi_Raw.dry Baseline:BaselineRaw Hevi.dry Parse,Gloss,Translation"
    "dry merge HkNb4.dry Baseline,Translation HkNb4_Raw.dry *"
    "dry merge Hevi_Raw.dry Baseline:BaselineRaw/BaselineToClean,Translation:TranslationRaw/TranslationToClean Hevi.dry *"

    # TODO have a "row label" for which file's residues to keep, do not allow mixing of residues from multiple files
    # TODO error if the files don't have the same number of lines and/or the designations don't match entirely

    if output_fp is None:
        # print the output instead so user can pipe it to less or whatever
        raise NotImplementedError
    else:
        # output it to the file
        raise NotImplementedError
