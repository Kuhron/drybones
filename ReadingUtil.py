# helper functions for getting contents of texts for display to user
# but NOT for actually doing any displaying



def get_text_file_from_text_name(text_name):
    return f"{text_name}.txt"


def get_line_sets_from_text_name(text_name):
    fp = get_text_file_from_text_name(text_name)
    return get_line_sets_from_file(fp)


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
