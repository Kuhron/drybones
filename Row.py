# one row in a line
# e.g. the Morphemes row in line 34 of the text

from Cell import Cell


class Row:
    DELIMITER = "\t"
    def __init__(self, label, cells):
        assert type(label) is str
        self.label = label
        assert type(cells) is list
        assert all(type(x) is Cell for x in cells)
        self.cells = cells

    def __len__(self):
        return len(self.cells)
    
    def __iter__(self):
        return iter(self.cells)
    
    def __repr__(self):
        return repr([self.label] + self.cells)
    