# helper functions and constants for parsing texts
# but not the `dry parse` command itself, which is a group (groups/parse.py)

from drybones.Cell import Cell
from drybones.Row import Row

UNKNOWN_GLOSS = "?"
MORPHEME_DELIMITER = Cell.INTRA_CELL_DELIMITER
WORD_DELIMITER = Row.INTRA_ROW_DELIMITER

