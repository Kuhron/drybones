# don't bother inheriting from string, I tried that and it's a headache

class RowLabel:
    AFTER_LABEL_CHAR = ":"

    def __init__(self, string, aligned: bool):
        assert not any(x in string for x in [" ", "\t", "\n", "\r"]), "whitespace not allowed in row label"
        assert RowLabel.AFTER_LABEL_CHAR not in string, f"do not include '{RowLabel.AFTER_LABEL_CHAR}' when initializing row label"
        self.string = string
        self.aligned = aligned

    def is_aligned(self):
        return self.aligned

    def with_after_label_char(self):
        return self.string + RowLabel.AFTER_LABEL_CHAR
    
    def without_after_label_char(self):
        return self.string

    def __repr__(self):
        return f"<RowLabel {repr(self.without_after_label_char())}>"
    
    def __str__(self):
        return self.without_after_label_char()
    
    def __eq__(self, other):
        if type(other) is not RowLabel:
            return NotImplemented
        return self.string == other.string
    
    def __hash__(self):
        return hash(repr(self))


DEFAULT_LINE_DESIGNATION_LABEL = RowLabel("N", aligned=False)
DEFAULT_BASELINE_LABEL = RowLabel("Baseline", aligned=True)
DEFAULT_TRANSLATION_LABEL = RowLabel("Translation", aligned=False)
DEFAULT_PARSE_LABEL = RowLabel("Parse", aligned=True)
DEFAULT_GLOSS_LABEL = RowLabel("Gloss", aligned=True)
DEFAULT_MORPHEME_CLASS_LABEL = RowLabel("Class", aligned=True)
DEFAULT_WORD_GLOSS_LABEL = RowLabel("Wordgloss", aligned=True)
DEFAULT_WORD_CLASS_LABEL = RowLabel("Wordclass", aligned=True)

DEFAULT_ROW_LABELS = [
    DEFAULT_LINE_DESIGNATION_LABEL,
    DEFAULT_BASELINE_LABEL,
    DEFAULT_TRANSLATION_LABEL,
    DEFAULT_PARSE_LABEL,
    DEFAULT_GLOSS_LABEL,
    DEFAULT_MORPHEME_CLASS_LABEL,
    DEFAULT_WORD_GLOSS_LABEL,
    DEFAULT_WORD_CLASS_LABEL,
]

DEFAULT_ROW_LABELS_BY_STRING = {l.string: l for l in DEFAULT_ROW_LABELS}
DEFAULT_ALIGNED_ROW_LABELS = [l for l in DEFAULT_ROW_LABELS if l.is_aligned()]
