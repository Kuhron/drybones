# don't bother inheriting from string, I tried that and it's a headache

class RowLabel:
    AFTER_LABEL_CHAR = ":"

    def __init__(self, string, strip_colon=False):
        assert not any(x in string for x in [" ", "\t", "\n", "\r"]), "whitespace not allowed in row label"

        if strip_colon:
            # if there's a final colon, remove it silently, do this work for the user; if there's not one, no problem
            while string[-1] == RowLabel.AFTER_LABEL_CHAR:
                string = string[:-1]
        else:
            assert RowLabel.AFTER_LABEL_CHAR not in string, f"do not include '{RowLabel.AFTER_LABEL_CHAR}' when initializing row label"
        assert RowLabel.AFTER_LABEL_CHAR not in string
        self.string = string

    def with_after_label_char(self):
        return self.string + RowLabel.AFTER_LABEL_CHAR
    
    def without_after_label_char(self):
        return self.string

    def __repr__(self):
        return f"<RowLabel {repr(self.without_after_label_char())}>"
    
    def __str__(self):
        return self.without_after_label_char()


DEFAULT_ALIGNED_ROW_LABEL_STRS = ["Baseline", "Translation", "Parse", "Gloss"]
DEFAULT_ALIGNED_ROW_LABELS = [RowLabel(s) for s in DEFAULT_ALIGNED_ROW_LABEL_STRS]
