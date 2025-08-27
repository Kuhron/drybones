# objects holding information for each line/row/str/etc. that comes up as a result of `dry search`

from drybones.Line import Line
from drybones.Row import Row


class SearchResult:
    def __init__(self, string:str, row:Row, line:Line):
        self.string = string
        self.row = row
        self.line = line
    
    def to_detailed_display_str(self):
        s = "\nSearch result:\n"
        s += f"matched string: {self.string!r}\n"
        s += f"in row with label: {self.row.label.string!r}\n"
        s += "in line:\n"
        s += self.line.to_string_for_drybones_file() + "\n"
        return s
