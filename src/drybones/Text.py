# a text in the corpus, consisting of a series of lines

from typing import List
from pathlib import Path

from drybones.Line import Line


class Text:
    def __init__(self, name: str, lines: List[Line], residues: List[str], source_fp: Path):
        assert type(lines) is list
        assert all(type(x) is Line for x in lines)
        self.name = name
        self.lines = lines
        self.residues = residues
        self.source_fp = source_fp
