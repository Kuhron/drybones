from typing import List

from drybones.Row import Row
from drybones.RowLabel import RowLabel, DEFAULT_PARSE_LABEL, DEFAULT_GLOSS_LABEL, DEFAULT_BASELINE_LABEL
from drybones.Validation import Validated, Invalidated, InvalidationError

# all rows in the line have to have length N (alignable, e.g. glosses) or 1 (non-alignable, e.g. free translation of the whole line)

class Line:
    BEFORE_LINE = "┌------------┐\n"
    AFTER_LINE  = "\n└------------┘"

    def __init__(self, designation: str, rows: List[Row]):
        assert type(rows) is list
        assert all(type(x) is Row for x in rows)
        self.designation = designation
        self.rows = rows
        self.validate_row_lengths()
        self.row_by_label = self.construct_row_by_label()

    def construct_row_by_label(self):
        d = {}
        for r in self.rows:
            d[r.label] = r
        return d

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
        return f"<Line {self.designation} {self.rows!r}>"
    
    def __getitem__(self, index):
        if type(index) is not RowLabel:
            raise TypeError(f"invalid type for subscripting Line: {type(index)}")
        return self.row_by_label.get(index)
    
    def has_baseline(self) -> bool:
        baseline_row = self[DEFAULT_BASELINE_LABEL]
        return baseline_row is not None

    def is_parsed_and_glossed(self) -> bool:
        return DEFAULT_PARSE_LABEL in self.row_by_label and DEFAULT_GLOSS_LABEL in self.row_by_label
    
    def to_string_for_drybones_file(self) -> str:
        strs = []
        for row in self.rows:
            s = row.to_str(with_label=True)
            strs.append(s)
        return Line.BEFORE_LINE + "\n".join(strs) + Line.AFTER_LINE

    def get_all_row_labels(self, string=False):
        s = set(self.row_by_label.keys())
        if string:
            return {x.string for x in s}
        else:
            return s
