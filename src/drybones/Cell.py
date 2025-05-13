# the intersection of a single line and a single chunk
# e.g. the morphemes of one wordform

# the strings in a cell are separated by '-' in the printout

class Cell:
    INTRA_CELL_DELIMITER = "-"

    def __init__(self, strs):
        self.strs = strs
        self.str = self.to_str()

    def to_str(self):
        if hasattr(self, "str"):
            return self.str
        return Cell.INTRA_CELL_DELIMITER.join(self.strs)
    
    def strip(self):
        return self.to_str().strip()
    
    def __repr__(self):
        return f"<Cell {self.strs}>"

    def __str__(self):
        return self.to_str()
    