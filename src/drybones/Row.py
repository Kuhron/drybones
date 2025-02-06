# one row in a line
# e.g. the Morphemes row in line 34 of the text

from typing import List

from drybones.Cell import Cell
from drybones.RowLabel import RowLabel


class Row:
    DELIMITER = "\t"
    def __init__(self, label:RowLabel, cells:List[Cell]):
        assert type(label) is RowLabel
        self.label = label
        assert type(cells) is list
        assert all(type(x) is Cell for x in cells)
        self.cells = cells

    def __len__(self):
        return len(self.cells)
    
    def __iter__(self):
        return iter(self.cells)
    
    def __repr__(self):
        return f"<Row label={self.label.without_colon()} {self.cells}>"
