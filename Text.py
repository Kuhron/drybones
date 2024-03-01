# a text in the corpus, consisting of a series of lines

from Line import Line


class Text:
    def __init__(self, lines):
        assert type(lines) is list
        assert all(type(x) is Line for x in lines)
        self.lines = lines
