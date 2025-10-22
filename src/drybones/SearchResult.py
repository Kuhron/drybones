# objects holding information for each line/row/str/etc. that comes up as a result of `dry search`

from typing import List, Tuple

from drybones.ColorUtil import SUB_HIGHLIGHT
from drybones.Line import Line
from drybones.Row import Row


class SearchResult:
    def __init__(self, string:str, spans:List[Tuple[int,int]], row:Row, line:Line):
        self.string = string
        self.spans = verify_spans(spans)  # start and end indices for every place where the search matched
        self.row = row
        self.line = line
    
    def to_detailed_display_string(self):
        s = "\nSearch result:\n"
        s += f"matched string: {self.string!r}\n"
        s += f"in row with label: {self.row.label.string!r}\n"
        s += "in line:\n"
        s += self.line.to_string_for_drybones_file() + "\n"
        return s

    def get_highlighted_string(self):
        # 012345678901234
        # asdfghjkl
        # a[s]dfghjkl
        # a[s]d[fg]hjkl
        # a[s]d[fg][h]jkl
        # 012345678901234

        s = self.string
        offset = 0
        for start, end in self.spans:
            orig = self.string[start:end]  # the spans are not offset, so get the substring from the original string
            hl = SUB_HIGHLIGHT(orig)
            len_diff = len(hl) - len(orig)

            # assume the spans are in order, so we are always getting start and end indices that are after the portion causing the offset, and thus their indices will be offset
            start_in_s = start + offset
            end_in_s = end + offset

            s = s[:start_in_s] + hl + s[end_in_s:]

            # offset goes up if we add chars when highlighting the substring
            offset += len_diff
            if offset < 0:
                raise ValueError(f"offset went negative: {offset}\nin SearchResult: {self.to_detailed_display_string()}")
        
        return s



def verify_spans(spans: List[Tuple[int, int]]):
    # make sure they don't overlap, and put them in order
    last_span = None
    for i, span in enumerate(spans):
        start, end = span
        if not (start < end):
            raise ValueError(f"start of span must be strictly less than end, but got: {span}")
        if last_span is not None:
            last_start, last_end = last_span
            # already checked that start < end for the last span
            # check that the two spans don't overlap
            if not (start >= last_end):
                raise ValueError(f"the start of one span must be >= the end of the previous one, but got overlapping spans: {spans[i-1:i+1]}")
        last_span = span
    
    return sorted(spans)
