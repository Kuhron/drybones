import click
from typing import List

from drybones.Cell import Cell
from drybones.Row import Row
from drybones.RowLabel import RowLabel, DEFAULT_PARSE_LABEL, DEFAULT_GLOSS_LABEL, DEFAULT_BASELINE_LABEL, DEFAULT_LINE_DESIGNATION_LABEL
from drybones.Validation import Validated, Invalidated, InvalidationError

# all rows in the line have to have length N (alignable, e.g. glosses) or 1 (non-alignable, e.g. free translation of the whole line)

class Line:
    BEFORE_LINE = "┌------------┐\n"
    AFTER_LINE  = "\n└------------┘"

    def __init__(self, designation: str, rows: List[Row]):
        assert type(rows) is list
        assert all(type(x) is Row for x in rows)
        self.designation = designation
        self.designation_row = Line.create_designation_row(self.designation)
        Line.check_no_designation_in_content_rows(rows)
        self.rows = rows
        self.validate_row_lengths()
        self.row_by_label = self.construct_row_by_label()
        self.row_label_by_string = self.construct_row_label_by_string()

    def construct_row_by_label(self):
        d = {}
        for r in self.rows:
            d[r.label] = r
        return d
    
    def construct_row_label_by_string(self):
        d = {}
        for label in self.row_by_label.keys():
            s = label.string
            assert s not in d, f"duplicate label string {s!r}"
            d[s] = label
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
        if type(index) is RowLabel:
            return self.row_by_label.get(index)
        elif type(index) is str:
            label = self.row_label_by_string.get(index)
            if label is None:
                raise KeyError(f"no row label found with string {index!r}")
            return self.row_by_label.get(label)
        else:
            raise TypeError(f"invalid type for subscripting Line: {type(index)}")
    
    def has_baseline(self) -> bool:
        baseline_row = self[DEFAULT_BASELINE_LABEL]
        return baseline_row is not None

    def is_parsed_and_glossed(self) -> bool:
        return DEFAULT_PARSE_LABEL in self.row_by_label and DEFAULT_GLOSS_LABEL in self.row_by_label
    
    def to_string_for_drybones_file(self) -> str:
        strs = []
        for row in [self.designation_row] + self.rows:
            s = row.to_str(with_label=True)
            strs.append(s)
        return Line.BEFORE_LINE + "\n".join(strs) + Line.AFTER_LINE

    def get_all_row_labels(self, string=False, exclude_designation=True):
        s = set(self.row_by_label.keys())
        if exclude_designation:
            s.remove(DEFAULT_LINE_DESIGNATION_LABEL)
        if string:
            return {x.string for x in s}
        else:
            return s

    @staticmethod
    def create_designation_row(designation_str) -> Row:
        cells = [Cell(strs=[designation_str])]
        row = Row(label=DEFAULT_LINE_DESIGNATION_LABEL, cells=cells)
        return row
    
    @staticmethod
    def check_no_designation_in_content_rows(rows):
        for row in rows:
            if row.label == DEFAULT_LINE_DESIGNATION_LABEL:
                click.echo("Cannot initiate line with designation row as one of the content rows")
                raise click.Abort()

