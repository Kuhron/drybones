# a vertical column in the parsing
# a wordform and its morphemes and its lexemes and its glosses, etc.

from Cell import Cell


class Column:
    def __init__(self, cells):
        assert type(cells) is list
        assert all(type(x) is Cell for x in cells)
        self.cells = cells

# everything in the column needs to be split into N strs (e.g. morphemes) or 1 str (e.g. wordform)
