# helping figure out what user meant to type

import click

from Validation import Validated, Invalidated


# copied from https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
def levenshtein(seq1, seq2):
    big_length = 1000
    if max(len(seq1), len(seq2)) > big_length:
        raise Exception("Levenshtein function will be memory-intensive with long strings. Your strings have lengths {} and {}.".format(len(seq1), len(seq2)))
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    # matrix = np.zeros ((size_x, size_y))
    matrix = [[0 for y in range(size_y)] for x in range(size_x)]
    for x in range(size_x):
        matrix [x][0] = x
    for y in range(size_y):
        matrix [0][y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x][y] = min(
                    matrix[x-1][y] + 1,
                    matrix[x-1][y-1],
                    matrix[x][y-1] + 1
                )
            else:
                matrix [x][y] = min(
                    matrix[x-1][y] + 1,
                    matrix[x-1][y-1] + 1,
                    matrix[x][y-1] + 1
                )
    # print (matrix)
    return (matrix[size_x - 1][size_y - 1])


def normalized_levenshtein(x, y):
    d = levenshtein(x, y)
    max_d = max(len(x), len(y))
    return d / max_d


def validate_string(s, options, case_sensitive=False):
    if case_sensitive:
        s_test = s
        options_test = options
    else:
        s_test = s.lower()
        options_test = [x.lower() for x in options]
        if len(set(options_test)) != len(options_test):
            # find which ones conflict
            groups = get_ambiguous_groups(options, lambda x: x.lower())
            click.echo(f"Cannot use case-insensitive search when these options depend on case:\n" + "\n  ".join(", ".join(group) for group in groups), err=True)
            return None
    
    options_test_to_option = dict(zip(options_test, options))
    if s_test in options_test:
        return Validated(options_test_to_option[s_test])
    else:
        # return a list of top matches so the function calling this can display them with whatever custom message it wants
        # e.g. "X is not a valid {text name / directory / command}, did you mean {options}?"
        d = {}
        for x_test, x in zip(options_test, options):
            d[x] = normalized_levenshtein(s_test, x_test)
        top_n = 5
        tups = sorted(d.items(), key=lambda kv: kv[1])
        tups = tups[:top_n]
        top_options = [tup[0] for tup in tups]
        return Invalidated(top_options)


def get_ambiguous_groups(options, collapse_function):
    val_to_group = {}
    for x in options:
        val = collapse_function(x)
        if val not in val_to_group:
            val_to_group[val] = []
        val_to_group[val].append(x)
    return [group for group in val_to_group.values() if len(group) > 1]
