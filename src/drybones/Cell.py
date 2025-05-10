# the intersection of a single line and a single chunk
# e.g. the morphemes of one wordform

# the strings in a cell are separated by '-' in the printout

class Cell:
    DELIMITER = "-"

    def __init__(self, strs):
        self.strs = strs

    def to_str(self):
        return Cell.DELIMITER.join(self.strs)
    
    def strip(self):
        return self.to_str().strip()
    
    def __repr__(self):
        return f"<Cell {self.strs}>"

    def __str__(self):
        return self.to_str()
    