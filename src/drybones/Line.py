from typing import List

from drybones.Row import Row
from drybones.Validation import Validated, Invalidated, InvalidationError

# all rows in the line have to have length N (alignable, e.g. glosses) or 1 (non-alignable, e.g. free translation of the whole line)

class Line:
    BEFORE_LINE = "┌------------┐\n"
    AFTER_LINE  = "└------------┘\n"

    def __init__(self, number: int, rows: List[Row]):
        assert type(rows) is list
        assert all(type(x) is Row for x in rows)
        self.number = number
        self.rows = rows
        self.validate_row_lengths()

    def validate_row_lengths(self):
        lens = sorted(set(len(x) for x in self.rows))
        if len(lens) in [0, 1]:
            # fine
            return
        elif len(lens) > 2:
            # this kind of validation function, where we raise errors, is for drybones-internal stuff, something is not working in the machinery
            # if it's about validating stuff the user is doing, then return Validated or Invalidated objects and print messages to stderr
            raise InvalidationError(f"too many row lengths, need 0 to 2: {lens}")
        else:
            one, n = lens
            if one != 1:
                raise InvalidationError(f"lengths should all be 1 or N, where N > 1 and is the same throughout the line, got: {lens}")
            else:
                return

    def __iter__(self):
        return iter(self.rows)
    
    def __len__(self):
        return len(self.rows)
    
    def __repr__(self):
        return repr(self.rows)
    