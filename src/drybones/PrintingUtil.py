# helper functions for displaying text contents to the user

import click
import os
import numbers
from typing import List

import drybones.ReadingUtil as ru
from drybones.DebuggingUtil import get_counter_string
from drybones.Line import Line
from drybones.RowLabel import RowLabel, DEFAULT_LINE_DESIGNATION_LABEL


def get_print_string_of_partial_row(row, column_indices):
    # for non-aligned rows, show them in every column index group
    # for the line number, can put a parenthetical about which group we're in, e.g. "Kaikai 240 (1/3)"
    # need row label always
    raise NotImplementedError


def get_print_strings_of_line(line: Line):
    terminal_size = os.get_terminal_size()
    right_padding = 1
    terminal_width = terminal_size.columns - right_padding
    n_cells_per_row = max(len(row) for row in line)
    cell_lists = []
    row_labels = []
    for row in line:
        these_cells = [cell.strip() for cell in row] + ["" for i in range(n_cells_per_row - len(row))]
        assert len(these_cells) == n_cells_per_row
        cell_lists.append(these_cells)
        label = row.label
        row_labels.append(label)

    # makes more sense to have the row object know if it's aligned, rather than passing around a list of which labels are aligned
    is_aligned_by_index = {j: row.is_aligned() for j, row in enumerate(line)}

    max_label_len = max(len(label.with_after_label_char()) for label in row_labels)
    max_seg_len_by_index = {}
    for i in range(n_cells_per_row):
        display_widths = []
        for j, these_cells in enumerate(cell_lists):
            if is_aligned_by_index[j] is True:
                display_width = get_display_width(these_cells[i])
                display_widths.append(display_width)
        if len(display_widths) == 0:
            this_max_seg_len = 0  # TODO is this a good idea or should it be None? idk, see what happens, but this could be a source of bugs! it's low stakes because it's just for display but still, #BUGMAKER <-- for ctrl-f'ing for bad/uninformed choices I made that I knew were potential causes of future bugs
        else:
            this_max_seg_len = max(display_widths)
        max_seg_len_by_index[i] = this_max_seg_len
    
    after_label_delim = " "
    general_delim = " | "  # something clearly dividing but not too wide and not intrusive-looking
    after_label_delim_width = get_display_width(after_label_delim)
    general_delim_width = get_display_width(general_delim)
    column_index_groupings = get_column_index_groupings(n_cells_per_row, max_label_len, max_seg_len_by_index, after_label_delim_width, general_delim_width, terminal_width)
    desig_str = line.designation_row.to_str(with_label=True)
    content_strs = get_print_strings_of_line_helper_using_column_index_groupings(column_index_groupings, cell_lists, is_aligned_by_index, after_label_delim, general_delim, max_seg_len_by_index, row_labels)

    strs = [desig_str] + content_strs

    # debug
    debug_strs = [
        f"{n_cells_per_row = }, {terminal_width = }",
        f"{max_seg_len_by_index = }",
    ]
    # strs = debug_strs + strs

    return strs


def get_print_strings_of_line_helper_using_column_index_groupings(column_index_groupings, cell_lists, is_aligned_by_index, after_label_delim, general_delim, max_seg_len_by_index, row_labels):
    strs = []
    group_delim = "- - - - - - - -"
    for column_index_grouping in column_index_groupings:
        for row_i, these_cells in enumerate(cell_lists):
            label_str = row_labels[row_i].with_after_label_char()
            s = label_str + after_label_delim
            # click.echo(f"initial s   = {show_whitespace(s)}")
            if is_aligned_by_index[row_i]:
                for i in column_index_grouping:
                    s += these_cells[i].ljust(max_seg_len_by_index[i] + sum(is_zero_width(c) for c in these_cells[i]))
                    # click.echo(f"plus cell   = {show_whitespace(s)}")
                    following_delim = "" if i == column_index_grouping[-1] else general_delim
                    s += following_delim
                    # click.echo(f"plus delim  = {show_whitespace(s)}")
                    # s = show_whitespace(s)
            else:
                if sum(len(x) > 0 for x in these_cells) > 2:
                    click.echo(f"\nError: non-aligned row shouldn't have any cells other than label and content.\nFor label {label_str!r}, got {these_cells}", err=True)
                    raise click.Abort()
                s += after_label_delim.join(these_cells)
                # click.echo(f"non-aligned = {show_whitespace(s)}")
            strs.append(s)
            # strs.append(get_counter_string(s))  # debug
        strs.append(group_delim)
    assert strs[-1] == group_delim
    strs = strs[:-1]
    # click.echo(strs)
    # input("a")
    return strs


def get_column_index_groupings(n_cells_per_row, max_label_len, max_seg_len_by_index, after_label_delim_width, general_delim_width, terminal_width):
    column_index_groupings = []  # which indices to group together since they don't exceed the terminal width
    # if a single field exceeds terminal width, just put it in a group by itself and let it overflow when printing

    # click.echo(f"{n_cells_per_row = }, {terminal_width = }")
    # click.echo(f"{max_seg_len_by_index = }")
    # delim_length_after_column_index = dict([(i, (get_display_width(after_label_delim) if i == 0 else 0 if i == n_cells_per_row-1 else get_display_width(general_delim))) for i in range(n_cells_per_row)])
    # cumsum = dict_cumsum(max_seg_len_by_index, extra_addends=delim_length_after_column_index)
    # click.echo(f"cumsum: {cumsum}")

    str_start_width = max_label_len + after_label_delim_width  # every grouping starts with at least this
    current_sum_width = str_start_width
    current_grouping = []
    for i in range(n_cells_per_row):
        # add this field to current grouping no matter what (if it's longer than the terminal width, it'll just be in a group by itself)
        current_grouping.append(i)
        w = max_seg_len_by_index[i]
        delim_width = after_label_delim_width if i == 0 else general_delim_width
        following_delim_width = delim_width if i != n_cells_per_row - 1 else 0
        current_sum_width += w

        # if delimiter and next field both fit, then keep this grouping, otherwise make a new one
        next_sum_width = current_sum_width + following_delim_width + (0 if i == n_cells_per_row - 1 else max_seg_len_by_index[i+1])
        if next_sum_width <= terminal_width:
            # no issue, keep with the current grouping
            pass
        else:
            # make a new grouping
            column_index_groupings.append(current_grouping)
            current_grouping = []
            current_sum_width = str_start_width
    if current_grouping != []:
        column_index_groupings.append(current_grouping)

    # click.echo(f"created {column_index_groupings = }")

    # debug
    # for grouping in column_index_groupings:
        # group_cumsum = dict_cumsum(sub_dict(max_seg_len_by_index, grouping), extra_addends=delim_length_after_column_index)
        # click.echo(f"group cumsum: {group_cumsum}")
    
    return column_index_groupings


def sub_dict(d, keys):
    return {k: d[k] for k in keys}


def dict_cumsum(d, extra_addends=None):
    if type(extra_addends) is dict:
        pass  # all good
    elif isinstance(extra_addends, numbers.Number):
        # add the same number every time
        extra_addends = {k: extra_addends for k in d}
    else:
        raise TypeError(type(extra_addends))

    s = {}
    total = 0


    for k in sorted(d.keys()):
        total += d[k] + extra_addends[k]
        s[k] = total
    return s


def get_print_string_of_lines(lines: List[Line]):
    s = ""
    for line in lines:
        strs = get_print_strings_of_line(line)
        for x in strs:
            s += x + "\n"
        s += "\n"
    return s


def print_line(line):
    strs = get_print_strings_of_line(line)
    for s in strs:
        click.echo(s)


def print_text_line_by_line(fp):
    lines = ru.get_lines_and_residues_from_drybones_file(fp)
    for line in lines:
        print_line(line)
        click.echo()
        click.prompt("press enter to continue")
    click.echo(f"finished reading text at {fp}", err=True)


def print_lines_in_terminal(lines):
    click.echo(get_print_string_of_lines(lines))


def print_lines_in_pager(lines: List[Line]):
    click.echo_via_pager(get_print_string_of_lines(lines))


def get_display_width(s):
    # don't count zero-width chars
    return sum(not is_zero_width(c) for c in s)


def show_whitespace(s):
    return s.replace(" ", "\u00b7").replace("\t", "\u2014").replace("\n", "\u21b5")


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

    dry_fnames = sorted([x for x in os.listdir(text_dir) if x.endswith(".dry")])
    for fname in dry_fnames:
        fp = os.path.join(text_dir, fname)
        print_text_line_by_line(fp)
