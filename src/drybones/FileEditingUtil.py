import click
from hashlib import sha256

from drybones.ReadingUtil import get_lines_and_residues_from_drybones_file


def setup_file_editing_operation(drybones_fp, overwrite):
    if overwrite:
        new_drybones_fp = drybones_fp

        # get initial hash so later we can check if the file changed during our operation (e.g. I'm editing it in VS Code while also parsing in DryBones, then DryBones will overwrite whatever I did in VS Code; this has happened to me enough times now as of 2025-08-21 that I'm sick of it)
        with open(drybones_fp, "rb") as f:
            contents = f.read()
        initial_hash = sha256(contents).hexdigest()
    else:
        new_drybones_fp = (lambda p: p.parent / (p.stem + "_dryout" + p.suffix))(drybones_fp)
        if new_drybones_fp.exists():
            raise FileExistsError(new_drybones_fp)
        
        # don't need to worry about overwriting the input file because we're writing to a different path
        initial_hash = None

    lines, residues_by_location = get_lines_and_residues_from_drybones_file(drybones_fp)
    line_designations_in_order = [l.designation for l in lines]
    new_lines_by_designation = {l.designation: l for l in lines}

    return new_drybones_fp, lines, residues_by_location, line_designations_in_order, new_lines_by_designation, initial_hash


def finish_file_editing_operation(new_drybones_fp, residues_by_location, line_designations_in_order, new_lines_by_designation, initial_hash):
    new_lines = [new_lines_by_designation[desig] for desig in line_designations_in_order]
    output_updated_lines(new_lines, residues_by_location, new_drybones_fp, initial_hash)


def output_updated_lines(new_lines, residues_by_location, new_drybones_fp, initial_hash):
    # construct the output string to replace the input file's contents
    # DON'T RE-SORT! let it stay in user's order
    s_to_write = ""
    locations_checked = set()
    for i, l in enumerate(new_lines):
        location = i-0.5
        locations_checked.add(location)
        residue_before_line = residues_by_location.get(location, "")
        line_str = l.to_string_for_drybones_file() 
        s_to_write += residue_before_line + line_str
    final_location = i+0.5  # actually using the final value of a loop variable outside the loop? crazy
    locations_checked.add(final_location)
    residue_at_end = residues_by_location.get(final_location, "")
    s_to_write += residue_at_end
    assert set(residues_by_location.keys()) - locations_checked == set(), "failed to check for residues at some locations"

    if initial_hash is not None:
        # enforce that the file's contents haven't changed between reading and this writing operation
        # otherwise write to a non-preexisting filepath and tell the user where it is
        # only makes sense to check this if we are writing to the same file we read from
        with open(new_drybones_fp, "rb") as f:
            contents = f.read()
        final_hash = sha256(contents).hexdigest()
        if final_hash != initial_hash:
            click.echo(f"Warning: file has been changed since reading: {new_drybones_fp}")
            original_new_drybones_fp = new_drybones_fp
            i = 0
            limit = 10000
            while new_drybones_fp.exists():
                i += 1
                new_drybones_fp = (lambda p: p.parent / (p.stem + f"_{i}" + p.suffix))(original_new_drybones_fp)

                if i > limit:
                    click.echo(f"something is very wrong here, because you probably don't have {limit} files that conflict with `new_drybones_fp`", err=True)
                    raise click.Abort()
            click.echo(f"Writing instead to another filepath: {new_drybones_fp}")

    with open(new_drybones_fp, "w") as f:
        f.write(s_to_write)
