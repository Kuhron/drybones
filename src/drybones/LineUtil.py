from typing import List, Dict

from drybones.Line import Line
from drybones.LineDesignation import LineDesignation


def get_line_designation_to_line_dict_from_list(lines: List[Line]) -> Dict[LineDesignation, Line]:
    designation_to_line = {}
    for l in lines:
        assert l.designation not in designation_to_line, f"duplicate line designation: {l.designation}"
        designation_to_line[l.designation] = l
    return designation_to_line
