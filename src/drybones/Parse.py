# class for a way of dividing a word into morphemes

from drybones.Cell import Cell

from typing import List


class Parse:
    def __init__(self, morpheme_strs: List[str]):
        self.morpheme_strs = morpheme_strs
        self.str = self.to_str()

    def to_str(self):
        if hasattr(self, "str"):
            return self.str
        return Cell.INTRA_CELL_DELIMITER.join(self.morpheme_strs)

    def __eq__(self, other):
        if type(other) is not Parse:
            return NotImplemented
        return self.str == other.str
    
    def __hash__(self):
        return hash(self.str)
