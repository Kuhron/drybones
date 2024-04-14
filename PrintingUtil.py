# helper functions for displaying text contents to the user

import click
import os
import numbers

import ReadingUtil as ru

DEFAULT_ROW_LABEL_FOR_LINE_LABEL = "Ln"


def get_print_string_of_partial_row(row, column_indices):
    # for non-aligned rows, show them in every column index group
    # for the line number, can put a parenthetical about which group we're in, e.g. "Kaikai 240 (1/3)"
    # need row label always
    is_line_label = row.label.without_colon() == DEFAULT_ROW_LABEL_FOR_LINE_LABEL  # later should probably configure this instead of hardcoding



def get_print_strings_of_line(line, labels_of_aligned_rows):
    terminal_size = os.get_terminal_size()
    right_padding = 1
    terminal_width = terminal_size.columns - right_padding
    print(terminal_width)
    print("*"*(terminal_width-3)+"321")
    # input("a")
    n_cells_per_row = max(len(row) for row in line)
    cells = []
    row_labels = []
    n_rows = len(line)
    for row in line:
        these_cells = [cell.strip() for cell in row] + ["" for i in range(n_cells_per_row - len(row))]
        assert len(these_cells) == n_cells_per_row
        cells.append(these_cells)
        label = row.label
        row_labels.append(label)
    is_aligned_by_index = {j: (row_labels[j].without_colon() in labels_of_aligned_rows) for j in range(n_rows)}
    # the labels are also aligned
    max_label_len = max(len(label.with_colon()) for label in row_labels)
    max_seg_len_by_index = {i: max(get_display_width(these_cells[i]) for j, these_cells in enumerate(cells) if is_aligned_by_index[j] is True) for i in range(n_cells_per_row)}

    after_label_delim = " "
    general_delim = " | "  # something clearly dividing but not too wide and not intrusive-looking
    after_label_delim_width = get_display_width(after_label_delim)
    general_delim_width = get_display_width(general_delim)
    column_index_groupings = get_column_index_groupings(n_cells_per_row, max_label_len, max_seg_len_by_index, after_label_delim_width, general_delim_width, terminal_width)
    strs = get_print_strings_helper_using_column_index_groupings(column_index_groupings, cells, is_aligned_by_index, after_label_delim, general_delim, max_seg_len_by_index, row_labels)
    return strs


def get_print_strings_helper_using_column_index_groupings(column_index_groupings, cells, is_aligned_by_index, after_label_delim, general_delim, max_seg_len_by_index, row_labels):
    strs = []
    group_delim = "- - - - - - - -"
    for column_index_grouping in column_index_groupings:
        for row_i, these_cells in enumerate(cells):
            label = row_labels[row_i].with_colon()
            s = label + after_label_delim
            if is_aligned_by_index[row_i]:
                for i in column_index_grouping:
                    s += these_cells[i].ljust(max_seg_len_by_index[i] + sum(is_zero_width(c) for c in these_cells[i]))
                    following_delim = "" if i == column_index_grouping[-1] else after_label_delim if i == 0 else general_delim
                    s += following_delim
            else:
                assert sum(len(x) > 0 for x in these_cells) <= 2, f"non-aligned row shouldn't have any cells other than label and content, got {these_cells}"
                s += after_label_delim.join(these_cells)
            strs.append(s)
            strs.append(get_counter_string(s))
        strs.append(group_delim)
    assert strs[-1] == group_delim
    strs = strs[:-1]
    return strs


def get_counter_string(s):
    # get a string that helps me see how many chars long something is
    n = len(s)
    if n == 0:
        return "0"
    elif n <= 9:
        return "123456789"[:len(s)]
    elif n <= 999:
        # print the 10s such that their last 0 is at that length, and 5s halfway
        # e.g. for length 28: ....5...10....5...20....5678
        n_tens, rem = divmod(n, 10)
        ten_strs = []
        for i in range(n_tens):
            ten_str = str(i+1) + "0"
            template = "....5....."
            ten_strs.append(template[:-len(ten_str)] + ten_str)
        assert all(len(x) == 10 for x in ten_strs)
        assert all(x[-1] == "0" for x in ten_strs)
        res = "".join(ten_strs)

        if rem == 0:
            pass
        elif rem == 1:
            # need to put a 1 here but it's right next to the last 10, so we'll hack by changing the 0 to a o
            res = res[:-1] + "o"
            res += "1"
        elif rem < 5:
            res += "." * (rem - 1) + str(rem)
        elif rem == 5:
            res += "....5"
        elif rem == 6:
            res += "....s6"
        else:
            res += "....5" + "." * (rem - 5 - 1) + str(rem)

        return res
    else:
        raise Exception("too long")


def get_column_index_groupings(n_cells_per_row, max_label_len, max_seg_len_by_index, after_label_delim_width, general_delim_width, terminal_width):
    column_index_groupings = []  # which indices to group together since they don't exceed the terminal width
    # if a single field exceeds terminal width, just put it in a group by itself and let it overflow when printing

    # print(f"{n_cells_per_row = }, {terminal_width = }")
    # print(f"{max_seg_len_by_index = }")
    # delim_length_after_column_index = dict([(i, (get_display_width(after_label_delim) if i == 0 else 0 if i == n_cells_per_row-1 else get_display_width(general_delim))) for i in range(n_cells_per_row)])
    # cumsum = dict_cumsum(max_seg_len_by_index, extra_addends=delim_length_after_column_index)
    # print("cumsum:", cumsum)

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


    print(f"created {column_index_groupings = }")

    # for grouping in column_index_groupings:
        # group_cumsum = dict_cumsum(sub_dict(max_seg_len_by_index, grouping), extra_addends=delim_length_after_column_index)
        # print("group cumsum:", group_cumsum)
    # input("b")
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


def get_print_string_of_lines(lines, labels_of_aligned_rows):
    s = ""
    for line in lines:
        strs = get_print_strings_of_line(line, labels_of_aligned_rows)
        for x in strs:
            s += x + "\n"
        s += "\n"
    return s


def print_line(line, labels_of_aligned_rows):
    strs = get_print_strings_of_line(line, labels_of_aligned_rows)
    for s in strs:
        click.echo(s)


def print_text_line_by_line(fp, labels_of_aligned_rows):
    lines = ru.get_lines_from_file(fp)
    for line in lines:
        print_line(line, labels_of_aligned_rows)
        click.echo()
        click.prompt("press enter to continue")
    click.echo(f"finished reading text at {fp}", err=True)


def print_lines_in_terminal(lines, labels_of_aligned_rows):
    click.echo(get_print_string_of_lines(lines, labels_of_aligned_rows))


def print_lines_in_pager(lines, labels_of_aligned_rows):
    click.echo_via_pager(get_print_string_of_lines(lines, labels_of_aligned_rows))


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

    # labels_of_aligned_rows = ["Bl", "Mp", "Lx", "Gl", "Wc"]
    labels_of_aligned_rows = ["Bl", "Mp", "Gl", "Wc"]  # test what happens when we change which rows are aligned

    txt_fnames = sorted([x for x in os.listdir(text_dir) if x.endswith(".txt")])
    for fname in txt_fnames:
        fp = os.path.join(text_dir, fname)
        print_text_line_by_line(fp, labels_of_aligned_rows)
