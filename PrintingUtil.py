# helper functions for displaying text contents to the user

import click
import os

import ReadingUtil as ru


def get_print_strings_of_line(line, aligned_row_labels):
    for label in aligned_row_labels:
        assert ":" not in label, "row labels should be without colons when passed as parameter here"
    terminal_size = os.get_terminal_size()
    right_padding = 1
    n_cols = terminal_size.columns - right_padding
    n_cells_per_row = max(len(row) for row in line)
    cells = []
    row_labels = []
    n_rows = len(line)
    for row in line:
        these_cells = [cell.strip() for cell in row] + ["" for i in range(n_cells_per_row - len(row))]
        assert len(these_cells) == n_cells_per_row
        cells.append(these_cells)
        label = row.label
        assert label[-1] == ":", f"row label must end with colon in text file, got {label!r}"
        row_labels.append(label)
    is_aligned_by_index = {j: row_labels[j][:-1] in aligned_row_labels for j in range(n_rows)}
    max_seg_len_by_index = {i: max(get_display_width(these_cells[i]) for j, these_cells in enumerate(cells) if is_aligned_by_index[j] is True) for i in range(n_cells_per_row)}

    after_label_delim = " "
    general_delim = " | "  # something clearly dividing but not too wide and not intrusive-looking
    seg_index_groupings = []  # which indices to group together since they don't exceed the terminal width
    # if a single field exceeds terminal width, just put it in a group by itself and let it overflow when printing
    current_sum_width = 0
    current_grouping = []
    for i in range(n_cells_per_row):
        # add this field to current grouping no matter what (if it's longer than the terminal width, it'll just be in a group by itself)
        current_grouping.append(i)
        w = max_seg_len_by_index[i]
        delim = after_label_delim if i == 0 else general_delim
        following_delim_width = get_display_width(delim) if i == n_cells_per_row - 1 else 0
        current_sum_width += w

        # if delimiter and next field both fit, then keep this grouping, otherwise make a new one
        next_sum_width = current_sum_width + following_delim_width + (0 if i == n_cells_per_row - 1 else max_seg_len_by_index[i+1])
        if next_sum_width <= n_cols:
            # no issue, keep with the current grouping
            pass
        else:
            # make a new grouping
            seg_index_groupings.append(current_grouping)
            current_grouping = []
            current_sum_width = 0
    if current_grouping != []:
        seg_index_groupings.append(current_grouping)

    strs = []
    group_delim = "- - - - - - - -"
    for index_grouping in seg_index_groupings:
        for j, these_cells in enumerate(cells):
            label = these_cells[0]
            if is_aligned_by_index[j]:
                if 0 in index_grouping:
                    s = ""  # the label will be added as a normal field
                else:
                    s = label + after_label_delim  # put the label here myself so it will show in each grouping for lines that are longer than the terminal width

                for i in index_grouping:
                    s += these_cells[i].ljust(max_seg_len_by_index[i] + sum(is_zero_width(c) for c in these_cells[i]))
                    following_delim = "" if i == index_grouping[-1] else after_label_delim if i == 0 else general_delim
                    s += following_delim
            else:
                label = these_cells[0]
                assert sum(len(x) > 0 for x in these_cells) <= 2, f"non-aligned row shouldn't have any cells other than label and content, got {these_cells}"
                s = after_label_delim.join(these_cells)
            strs.append(s)
        strs.append(group_delim)
    assert strs[-1] == group_delim
    strs = strs[:-1]
    return strs


def get_print_string_of_lines(lines, aligned_row_labels):
    s = ""
    for line in lines:
        strs = get_print_strings_of_line(line, aligned_row_labels)
        for x in strs:
            s += x + "\n"
        s += "\n"
    return s


def print_line(line, aligned_row_labels):
    strs = get_print_strings_of_line(line, aligned_row_labels)
    for s in strs:
        click.echo(s)


def print_text_line_by_line(fp, aligned_row_labels):
    lines = ru.get_lines_from_file(fp)
    for line in lines:
        print_line(line, aligned_row_labels)
        click.echo()
        click.prompt("press enter to continue")
    click.echo(f"finished reading text at {fp}", err=True)


def print_lines_in_terminal(lines, aligned_row_labels):
    click.echo(get_print_string_of_lines(lines, aligned_row_labels))


def print_lines_in_pager(lines, aligned_row_labels):
    click.echo_via_pager(get_print_string_of_lines(lines, aligned_row_labels))


def get_display_width(s):
    # don't count zero-width chars
    return sum(not is_zero_width(c) for c in s)


def is_zero_width(c):
    assert len(c) == 1
    h = ord(c)
    # https://en.wikipedia.org/wiki/Combining_character#Unicode_ranges
    return (
        (0x0300 <= h <= 0x036f) or
        (0x1ab0 <= h <= 0x1aff) or
        (0x1dc0 <= h <= 0x1dff) or
        (0x20d0 <= h <= 0x20ff) or
        (0x2de0 <= h <= 0x2dff) or
        (0xfe20 <= h <= 0xfe2f)
    )

if __name__ == "__main__":
    text_dir = "/home/kuhron/Horokoi/DryBonesTesting/"
    # later can make this configurable or have the user open a project directory

    aligned_row_labels = ["Bl", "Mp", "Lx", "Gl", "Wc"]
    txt_fnames = sorted([x for x in os.listdir(text_dir) if x.endswith(".txt")])
    for fname in txt_fnames:
        fp = os.path.join(text_dir, fname)
        print_text_line_by_line(fp, aligned_row_labels)

