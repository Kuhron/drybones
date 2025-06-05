# ad-hoc script for converting from the output of langdoc-script-collection/video_audio_aligning.py --action=txt
# to DryBones-parseable format containing the exact same information
# from which I will then run `dry merge` to get the raw baseline and translation originating from the .eaf transcript
# and put those into the flexpy-exported DryBones text format
# so then ground-truth original baseline and translation strings will be in the same DryBones file as any parses/glosses already done in FLEx
# and from there I can continue parsing work solely in DryBones

from drybones.Line import Line
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("input_fp", type=Path)
parser.add_argument("-n", "--text_name", type=str, required=True)
args = parser.parse_args()
input_fp = args.input_fp
text_name = args.text_name

output_fp = input_fp.with_suffix(".dry")
print(f"converting {input_fp} into {output_fp}")

with open(input_fp) as f:
    contents = f.read()
group_strings = contents.split("----")
group_strings = [x.strip() for x in group_strings]
group_strings = [x for x in group_strings if len(x) > 0]

lines_to_write = []
for group_i, group_string in enumerate(group_strings):
    row_strings = [x.strip() for x in group_string.split("\n")]
    line_number_s, *other_row_strings = row_strings
    assert line_number_s[-1] == "."
    line_number = int(line_number_s[:-1])
    assert line_number == group_i + 1, line_number
    
    line_is_blank = True
    for s in other_row_strings:
        label, rest = s.split(":")
        if line_is_blank and rest.strip() != "":
            line_is_blank = False
    if line_is_blank:
        other_row_strings_to_write = [
            "Blank: -"
        ]
    else:
        other_row_strings_to_write = other_row_strings

    lines_to_write += [
        Line.BEFORE_LINE.strip(),
        f"N: {text_name} {line_number}",
    ] + other_row_strings_to_write + [
        Line.AFTER_LINE.strip(),
    ]

with open(output_fp, "w") as f:
    for l in lines_to_write:
        f.write(l + "\n")
