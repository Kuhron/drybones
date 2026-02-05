# for dealing with labels exported from Audacity


class AudacityLabel:
    def __init__(self, start_time_s: float, end_time_s: float, text: str):
        self.start_time_s = start_time_s
        self.end_time_s = end_time_s
        self.text = text
    
    @staticmethod
    def from_raw_row(s):
        if s.endswith("\n"):
            s = s[:-1]
        assert "\n" not in s, f"newline found in stripped Audacity label line: {s!r}"
        start_time_str, end_time_str, *texts = s.split("\t")
        text = "\t".join(texts)
        start_time_s = float(start_time_str)
        end_time_s = float(end_time_str)
        return AudacityLabel(start_time_s, end_time_s, text)


def get_audacity_labels_from_file(fp):
    with open(fp) as f:
        lines = f.read().splitlines()
    labels = [AudacityLabel.from_raw_row(s) for s in lines]
    return labels
