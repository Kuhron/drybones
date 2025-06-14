# don't bother inheriting from string, I tried that and it's a headache


class RowLabel:
    AFTER_LABEL_CHAR = ":"
    ALL_OTHER_ROWS_CHAR = "*"
    MULTIPLE_ROWS_SEPARATOR_CHAR = "/"
    RESIDUES_PSEUDO_LABEL = "residues"

    PROHIBITED_CHARS = [" ", "\t", "\n", AFTER_LABEL_CHAR, ALL_OTHER_ROWS_CHAR, MULTIPLE_ROWS_SEPARATOR_CHAR]
    PROHIBITED_STRINGS = [RESIDUES_PSEUDO_LABEL]

    def __init__(self, string, aligned: bool):
        assert not any(x in string for x in [" ", "\t", "\n", "\r"]), "whitespace not allowed in row label"
        assert RowLabel.AFTER_LABEL_CHAR not in string, f"do not include '{RowLabel.AFTER_LABEL_CHAR}' when initializing row label"
        assert not any(x in string for x in RowLabel.PROHIBITED_CHARS), f"the label {string!r} contains the following prohibited characters:\n{sorted(set(x for x in string if x in RowLabel.PROHIBITED_CHARS))}"
        assert string not in RowLabel.PROHIBITED_STRINGS, f"the label {string!r} is prohibited"
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
    
    def relabel(self, string):
        return RowLabel(string, self.aligned)


DEFAULT_LINE_DESIGNATION_LABEL = RowLabel("N", aligned=False)
DEFAULT_BASELINE_LABEL = RowLabel("Baseline", aligned=True)
DEFAULT_TRANSLATION_LABEL = RowLabel("Translation", aligned=False)
DEFAULT_PARSE_LABEL = RowLabel("Parse", aligned=True)
DEFAULT_GLOSS_LABEL = RowLabel("Gloss", aligned=True)
DEFAULT_MORPHEME_CLASS_LABEL = RowLabel("Class", aligned=True)
DEFAULT_WORD_GLOSS_LABEL = RowLabel("Wordgloss", aligned=True)
DEFAULT_WORD_CLASS_LABEL = RowLabel("Wordclass", aligned=True)
DEFAULT_PRODUCTION_LABEL = RowLabel("Production", aligned=False)
DEFAULT_JUDGMENT_LABEL = RowLabel("Judgment", aligned=False)

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
