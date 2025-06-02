# one row in a line
# e.g. the Morphemes row in line 34 of the text

from typing import List

from drybones.Cell import Cell
from drybones.RowLabel import RowLabel


class Row:
    INTRA_ROW_DELIMITER = " "
    
    def __init__(self, label: RowLabel, cells: List[Cell]):
        assert type(label) is RowLabel
        self.label = label
        assert type(cells) is list
        assert all(type(x) is Cell for x in cells)
        self.cells = cells

    def __len__(self):
        return len(self.cells)
    
    def __iter__(self):
        return iter(self.cells)

    def to_str(self, with_label: bool=True):
        raw_s = Row.INTRA_ROW_DELIMITER.join(cell.to_str() for cell in self.cells)
        if with_label:
            return self.label.with_after_label_char() + " " + raw_s
        else:
            return raw_s

    def __repr__(self):
        return f"<Row label={self.label.without_after_label_char()} {self.cells}>"

    def __str__(self, *args, **kwargs):
        return self.to_str(*args, **kwargs)
    
    def relabel(self, label: RowLabel):
        return Row(label, self.cells)
    