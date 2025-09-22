# class for a given parse along with a gloss for each of the parse's morphemes

import click

from drybones.Cell import Cell
from drybones.Parse import Parse


class WordAnalysis:
    def __init__(self, form_normal, form_key, parse, glosses):
        if len(parse.morpheme_strs) != len(glosses):
            s = "Cannot create WordAnalysis from parse and gloss list of unequal length.\n"
            s += f"Got {len(parse.morpheme_strs)} morphemes in parse: {parse.morpheme_strs}\n"
            s += f"Got {len(glosses)} glosses: {glosses}"
            click.echo(s, err=True)
            raise click.Abort()
        # self.form_raw = form_raw  # the exact string gotten from the cell in the drybones file, including punctuation, case, etc.
        self.form_normal = form_normal  # the linguistically-relevant form, excluding punctuation and case but including diacritics
        self.form_key = form_key  # the string used to look up this analysis, which may or may not exclude diacritics depending on options passed to command
        self.parse = parse
        self.glosses = glosses
        self.str = self.to_str()

    def to_str(self):
        if hasattr(self, "str"):
            return self.str
        form_str = self.form_normal
        parse_str = self.get_parse_str()
        gloss_str = self.get_gloss_str()
        s = f"{form_str} = {parse_str} = {gloss_str}"
        self.str = s
        return s
    
    def get_parse_str(self):
        return self.parse.str
    
    def get_gloss_str(self):
        return Cell.INTRA_CELL_DELIMITER.join(self.glosses)
    
    def __repr__(self):
        return self.to_str()

    def __key(self):
        # https://stackoverflow.com/a/2909119/7376935
        return (self.form_normal, self.form_key, self.parse, tuple(self.glosses))
    
    def __eq__(self, other):
        if type(other) is not WordAnalysis:
            return NotImplemented
        return self.__key() == other.__key()
    
    def __hash__(self):
        return hash(self.__key())
    