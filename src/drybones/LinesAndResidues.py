# a class for holding the contents of a text read from file
# want it as a class for type checker


from typing import List

from drybones.Line import Line
from drybones.LineUtil import get_line_designation_to_line_dict_from_list


class LinesAndResidues:
    def __init__(self, lines: List[Line], residues_by_location: dict):
        self.lines = lines
        self.designation_to_line = get_line_designation_to_line_dict_from_list(lines)
        self.residues_by_location = residues_by_location

    def __iter__(self):
        return iter([self.lines, self.residues_by_location])
    