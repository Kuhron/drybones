from drybones.ReadingUtil import get_lines_from_drybones_file


def setup_file_editing_operation(text_fp, overwrite):
    if overwrite:
        new_text_fp = text_fp
    else:
        new_text_fp = text_fp.parent / (text_fp.stem + "_dryout.dry")
        if new_text_fp.exists():
            raise FileExistsError(new_text_fp)

    lines, residues_by_location = get_lines_from_drybones_file(text_fp)
    line_designations_in_order = [l.designation for l in lines]
    new_lines_by_designation = {l.designation: l for l in lines}

    return new_text_fp, lines, residues_by_location, line_designations_in_order, new_lines_by_designation


def finish_file_editing_operation(new_text_fp, residues_by_location, line_designations_in_order, new_lines_by_designation):
    new_lines = [new_lines_by_designation[desig] for desig in line_designations_in_order]
    output_updated_lines(new_lines, residues_by_location, new_text_fp)


def output_updated_lines(new_lines, residues_by_location, new_text_fp):
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
    with open(new_text_fp, "w") as f:
        f.write(s_to_write)
