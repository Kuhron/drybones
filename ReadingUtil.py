# helper functions for getting contents of texts for display to user
# but NOT for actually doing any displaying

from Text import Text
from Line import Line
from Row import Row
from RowLabel import RowLabel
from Cell import Cell


def get_text_file_from_text_name(text_name):
    return f"{text_name}.txt"


def get_lines_from_text_name(text_name):
    fp = get_text_file_from_text_name(text_name)
    return get_lines_from_file(fp)


def get_lines_from_file(fp):
    # adjacent non-blank lines are in the same set
    raw_lines = get_raw_lines_from_file(fp, with_newlines=False)
    lines = []
    current_set = []
    for l in raw_lines:
        is_blank = l == ""
        if is_blank:
            if current_set == []:
                pass
            else:
                lines.append(current_set)
                current_set = []
        else:
            label_str, *strs = l.split("\t")
            label = RowLabel(label_str, strip_colon=True)
            cells = []
            for s in strs:
                cell = Cell(s.split("-"))
                cells.append(cell)
            line_obj = Row(label, cells)
            current_set.append(line_obj)
    if current_set != []:
        lines.append(current_set)
    lines = [Line(i+1, rows) for i, rows in enumerate(lines)]
    return lines


def get_raw_lines_from_file(fp, with_newlines=False):
    with open(fp) as f:
        lines = f.readlines()
    for l in lines:
        assert l[-1] == "\n"
    if with_newlines:
        return lines
    else:
        return [l[:-1] for l in lines]
