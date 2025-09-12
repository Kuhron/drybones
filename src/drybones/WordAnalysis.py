# class for a given parse along with a gloss for each of the parse's morphemes

import click

from drybones.Cell import Cell
from drybones.Parse import Parse


class WordAnalysis:
    def __init__(self, form, parse, glosses):
        if len(parse.morpheme_strs) != len(glosses):
            s = "Cannot create WordAnalysis from parse and gloss list of unequal length.\n"
            s += f"Got {len(parse.morpheme_strs)} morphemes in parse: {parse.morpheme_strs}\n"
            s += f"Got {len(glosses)} glosses: {glosses}"
            click.echo(s, err=True)
            raise click.Abort()
        self.form = form
        self.parse = parse
        self.glosses = glosses
        self.str = self.to_str()

    def to_str(self):
        if hasattr(self, "str"):
            return self.str
        s = self.get_parse_str() + " = " + self.get_gloss_str()
        return s
    
    def get_parse_str(self):
        return self.parse.str
    
    def get_gloss_str(self):
        return Cell.INTRA_CELL_DELIMITER.join(self.glosses)
    
    def __eq__(self, other):
        if type(other) is not WordAnalysis:
            return NotImplemented
        return self.parse == other.parse and self.glosses == other.glosses
    
    def __hash__(self):
        return hash(self.str)
    