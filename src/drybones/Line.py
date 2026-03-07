import click
from typing import List
from collections import defaultdict

from drybones.Cell import Cell
from drybones.LineDesignation import LineDesignation
from drybones.Row import Row
from drybones.RowLabel import RowLabel, DEFAULT_PARSE_LABEL, DEFAULT_GLOSS_LABEL, DEFAULT_BASELINE_LABEL, DEFAULT_LINE_DESIGNATION_LABEL, DEFAULT_DUPLICATE_LINE_LABEL
from drybones.Validation import Validated, Invalidated, InvalidationError

# all rows in the line have to have length N (alignable, e.g. glosses) or 1 (non-alignable, e.g. free translation of the whole line)

class Line:
    BEFORE_LINE = "┌------------┐\n"
    AFTER_LINE  = "\n└------------┘"

    def __init__(self, designation: LineDesignation, rows: List[Row]):
        assert type(rows) is list
        assert all(type(x) is Row for x in rows)
        assert type(designation) is LineDesignation
        self.designation = designation
        self.designation_row = Line.create_designation_row(self.designation)
        Line.check_no_designation_in_content_rows(rows)
        self.rows = rows
        self.validate_row_lengths()
        self.rows_by_label = self.construct_rows_by_label()
        self.row_label_by_string = self.construct_row_label_by_string()

    def construct_rows_by_label(self):
        d = {}
        for r in self.rows:
            label = r.label
            if label.can_occur_multiple_times_in_same_line():
                if label not in d:
                    d[label] = []
                d[label].append(r)
            else:
                assert label not in d, f"row with label {label} already present in line {self}"
                d[label] = r
        return d
    
    def construct_row_label_by_string(self):
        d = {}
        for label in self.rows_by_label.keys():
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
    
    def get(self, index, multiple:bool=False):
        # require function call to pass the "multiple" flag to show that the user knows the row label they are asking for could have multiple rows

        label = self.convert_get_index_to_row_label(index)
        if label is None:  # no row with this label exists in the line
            if multiple:
                return []
            else:
                return None
        else:  # the row(/s) exist(s/)
            if label.can_occur_multiple_times_in_same_line():
                assert multiple, f"the row label you asked for ({label}) can occur multiple times in the same line, so you need to pass the 'multiple' flag to Line.get() as a reminder to yourself that it will return a list"
                return self.rows_by_label.get(index, [])
            else:
                return self.rows_by_label.get(index, None)

    def __getitem__(self, index):
        raise Exception("use Line.get() instead of subscripting")

    def convert_get_index_to_row_label(self, index):
        if type(index) is RowLabel:
            return index
        elif type(index) is str:
            return self.row_label_by_string.get(index, None)
        else:
            raise TypeError(f"invalid index type for getting row from line: {type(index)}")

    def has_row_with_label(self, label) -> bool:
        val = self.get(label)
        if label.can_occur_multiple_times_in_same_line():
            assert type(val) is list
            return len(val) > 0
        else:
            return val != None

    def has_baseline(self) -> bool:
        return self.has_row_with_label(DEFAULT_BASELINE_LABEL)

    def is_parsed_and_glossed(self) -> bool:
        return DEFAULT_PARSE_LABEL in self.rows_by_label and DEFAULT_GLOSS_LABEL in self.rows_by_label
    
    def to_string_for_drybones_file(self) -> str:
        strs = []
        for row in [self.designation_row] + self.rows:
            s = row.to_str(with_label=True)
            strs.append(s)
        return Line.BEFORE_LINE + "\n".join(strs) + Line.AFTER_LINE

    def get_all_row_labels(self, string=False) -> set[RowLabel | str]:
        st = set(self.rows_by_label.keys())
        if string:
            return {x.string for x in st}
        else:
            return st
        
    def get_all_rows_including_designation(self):
        return [self.designation_row] + self.rows

    @staticmethod
    def create_designation_row(designation: LineDesignation) -> Row:
        designation_str = designation.to_str()
        cells = [Cell(strs=[designation_str])]
        row = Row(label=DEFAULT_LINE_DESIGNATION_LABEL, cells=cells)
        return row
    
    @staticmethod
    def check_no_designation_in_content_rows(rows):
        for row in rows:
            if row.label == DEFAULT_LINE_DESIGNATION_LABEL:
                click.echo("Cannot initiate line with designation row as one of the content rows")
                raise click.Abort()

    def is_duplicate(self):
        return self.has_row_with_label(DEFAULT_DUPLICATE_LINE_LABEL)
    