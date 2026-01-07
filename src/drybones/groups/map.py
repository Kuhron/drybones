import click
from pathlib import Path
from collections import defaultdict

from drybones.FileEditingUtil import setup_file_editing_operation, finish_file_editing_operation
from drybones.Line import Line
from drybones.Row import Row
from drybones.RowLabel import RowLabel


@click.command()
@click.argument("drybones_fp", required=True, type=Path)
@click.option("--mapping", "-m", required=True, type=str)
@click.option("--overwrite", "-w", type=bool, is_flag=True, help="Overwrite the input file. If false, a separate file will be created.")
@click.pass_context
def map(ctx, drybones_fp, mapping, overwrite):
    """Relabel rows."""
    mapping = parse_mapping_str(mapping)
    print(mapping)

    new_drybones_fp, lines, residues_by_location, line_designations_in_order, new_lines_by_designation, initial_hash = setup_file_editing_operation(drybones_fp, overwrite)
    all_label_strs = set()
    for line in lines:
        for row in line.rows:
            all_label_strs.add(row.label.string)
    inputs_not_found = sorted([x for x in mapping.keys() if x not in all_label_strs])
    if len(inputs_not_found) > 0:
        click.echo(f"these row labels were not found: {inputs_not_found}\nin {all_label_strs = }", err=True)
        raise click.Abort()

    verify_no_clashes(mapping, all_label_strs)

    for line in lines:
        new_rows = []
        for row in line.rows:
            new_label_str = mapping.get(row.label.string)
            if new_label_str is not None:
                new_label = row.label.relabel(new_label_str)
                new_row = Row(new_label, row.cells)
            else:
                new_row = row
            new_rows.append(new_row)
        new_line = Line(line.designation, new_rows)
        new_lines_by_designation[new_line.designation] = new_line

    finish_file_editing_operation(new_drybones_fp, residues_by_location, line_designations_in_order, new_lines_by_designation, initial_hash)


def parse_mapping_str(s):
    try:
        return dict([pair.split(":") for pair in s.split(",")])
    except ValueError:
        click.echo("mapping string must be comma-joined list of colon-separated pairs, e.g. 'TargetLang:Baseline,ContactLang:Translation'", err=True)
        raise click.Abort()


def verify_no_clashes(mapping: dict, all_label_strs: set):
    # impossible for one to map to many
    # what we are worried about is many mapping to one (name clash)
    # so check for one-to-one (input and output sets are same size)

    inputs = {x for x in all_label_strs}
    outputs = set()
    inputs_by_output = defaultdict(list)
    for inp in inputs:
        outp = mapping.get(inp, inp)
        outputs.add(outp)
        inputs_by_output[outp].append(inp)
    if len(outputs) != len(inputs):
        click.echo(f"This mapping causes some row labels to map to the same new row label. Each row label must map to a unique new label.", err=True)
        for outp, inps in sorted(inputs_by_output.items()):
            if len(inps) > 1:
                click.echo(f"- The following map to {outp!r}: {sorted(inps)}.", err=True)
        raise click.Abort()
