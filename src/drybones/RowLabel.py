# don't bother inheriting from string, I tried that and it's a headache

class RowLabel:
    def __init__(self, string, strip_colon=False):
        assert not any(x in string for x in [" ", "\t", "\n", "\r"]), "whitespace not allowed in row label"

        if strip_colon:
            # if there's a final colon, remove it silently, do this work for the user; if there's not one, no problem
            while string[-1] == ":":
                string = string[:-1]
        else:
            assert ":" not in string, "do not include colon when initializing row label"
        assert ":" not in string
        self.string = string

    def with_colon(self):
        return self.string + ":"
    
    def without_colon(self):
        return self.string

    def __repr__(self):
        return f"<RowLabel {repr(self.without_colon())}>"
