# a class for holding the contents of a text read from file
# want it as a class for type checker


class LinesAndResidues:
    def __init__(self, lines, residues_by_location):
        self.lines = lines
        self.residues_by_location = residues_by_location

    def __iter__(self):
        return iter([self.lines, self.residues_by_location])
    