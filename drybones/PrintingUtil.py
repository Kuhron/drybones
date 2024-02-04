import os
import random


def get_print_strings_of_line_set(line_set, aligned_line_labels):
    for label in aligned_line_labels:
        assert ":" not in label, "line labels should be without colons"
    terminal_size = os.get_terminal_size()
    right_padding = 1
    n_cols = terminal_size.columns - right_padding
    n_segments_per_line = max(len(l) for l in line_set)
    segments = []
    line_labels = []
    n_lines = len(line_set)
    for l in line_set:
        these_segments = [x.strip() for x in l] + ["" for i in range(n_segments_per_line - len(l))]
        assert len(these_segments) == n_segments_per_line
        segments.append(these_segments)
        label = these_segments[0]
        assert label[-1] == ":", f"line label must end with colon, got {label!r}"
        line_labels.append(label)
    is_aligned_by_index = {j: line_labels[j][:-1] in aligned_line_labels for j in range(n_lines)}
    max_seg_len_by_index = {i: max(get_display_width(these_segments[i]) for j, these_segments in enumerate(segments) if is_aligned_by_index[j] is True) for i in range(n_segments_per_line)}

    after_label_delim = " "
    general_delim = " | "  # or just a space, or something clearly dividing but not too wide and not intrusive-looking
    seg_index_groupings = []  # which indices to group together since they don't exceed the terminal width
    # if a single field exceeds terminal width, just put it in a group by itself and let it overflow when printing
    current_sum_width = 0
    current_grouping = []
    for i in range(n_segments_per_line):
        # add this field to current grouping no matter what (if it's longer than the terminal width, it'll just be in a group by itself)
        current_grouping.append(i)
        w = max_seg_len_by_index[i]
        delim = after_label_delim if i == 0 else general_delim
        following_delim_width = get_display_width(delim) if i == n_segments_per_line - 1 else 0
        current_sum_width += w
        # print(f"{i=}, {current_sum_width=}/{n_cols}, {w=}")

        # if delimiter and next field both fit, then keep this grouping, otherwise make a new one
        next_sum_width = current_sum_width + following_delim_width + (0 if i == n_segments_per_line - 1 else max_seg_len_by_index[i+1])
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
        for j, these_segments in enumerate(segments):
            label = these_segments[0]
            if is_aligned_by_index[j]:
                if 0 in index_grouping:
                    s = ""  # the label will be added as a normal field
                else:
                    s = label + after_label_delim  # put the label here myself so it will show in each grouping for line sets that are longer than the terminal width

                for i in index_grouping:
                    s += these_segments[i].ljust(max_seg_len_by_index[i])
                    following_delim = "" if i == index_grouping[-1] else after_label_delim if i == 0 else general_delim
                    s += following_delim
            else:
                label = these_segments[0]
                assert sum(len(x) > 0 for x in these_segments) <= 2, f"non-aligned line shouldn't have any segments other than label and content, got {these_segments}"
                s = after_label_delim.join(these_segments)
            strs.append(s)
        strs.append(group_delim)
    assert strs[-1] == group_delim
    strs = strs[:-1]
    return strs


def print_line_set(line_set, aligned_line_labels):
    strs = get_print_strings_of_line_set(line_set, aligned_line_labels)
    for s in strs:
        print(s)


def get_line_sets_from_file(fp):
    # adjacent non-blank lines are in the same set
    lines = get_lines_from_file(fp, with_newlines=False)
    line_sets = []
    current_set = []
    for l in lines:
        is_blank = l == ""  # hopefully there is no reason to have a line consisting of only whitespace? they should at least all have line labels
        if is_blank:
            if current_set == []:
                pass
            else:
                line_sets.append(current_set)
                current_set = []
        else:
            current_set.append(l.split("\t"))
    if current_set != []:
        line_sets.append(current_set)
    return line_sets


def get_lines_from_file(fp, with_newlines=False):
    with open(fp) as f:
        lines = f.readlines()
    for l in lines:
        assert l[-1] == "\n"
    if with_newlines:
        return lines
    else:
        return [l[:-1] for l in lines]


def print_text_line_by_line(fp, aligned_line_labels):
    line_sets = get_line_sets_from_file(fp)
    for line_set in line_sets:
        print_line_set(line_set, aligned_line_labels)
        print()
        input("press enter to continue")
    print(f"finished reading text at {fp}")


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
    text_dir = "/home/kuhron/Horokoi/TextDump/"
    # later can make this configurable or have the user open a project directory

    aligned_line_labels = ["Bl", "Mp", "Lx", "Gl", "Wc"]
    txt_fnames = sorted([x for x in os.listdir(text_dir) if x.endswith(".txt")])
    random.shuffle(txt_fnames)
    for fname in txt_fnames:
        fp = os.path.join(text_dir, fname)
        print_text_line_by_line(fp, aligned_line_labels)

