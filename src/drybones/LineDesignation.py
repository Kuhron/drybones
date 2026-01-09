

LINE_DESIGNATION_SEPARATOR = " "

class LineDesignation:
    def __init__(self, text_name, line_name):
        self.text_name = text_name
        self.line_name = line_name
    
    @staticmethod
    def from_row_text(s):
        text_name, line_name = s.split(LINE_DESIGNATION_SEPARATOR)
        return LineDesignation(text_name, line_name)
    
    def to_str(self):
        return f"{self.text_name}{LINE_DESIGNATION_SEPARATOR}{self.line_name}"

    def __repr__(self):
        return repr(self.to_str())

    def _get_tuple_for_overriding_methods(self):
        return (self.text_name, self.line_name)

    def __eq__(self, other):
        if type(other) is not LineDesignation:
            return NotImplemented
        return self._get_tuple_for_overriding_methods() == other._get_tuple_for_overriding_methods()
    
    def __hash__(self):
        return hash(self._get_tuple_for_overriding_methods())
    