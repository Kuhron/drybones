# functions about dealing with diacritics, converting between different representations of a character, matching regex while ignoring diacritics, etc.

import click
from pathlib import Path
from typing import List, Dict
import re

from drybones.DiacriticDict import DiacriticDict
from drybones.ProjectUtil import get_closest_parent_drybones_dir


DIACRITICS_CONF_FILENAME = "diacritics.conf"


def nop(*args, **kwargs):
    pass


def get_diacritics_conf_fp():
    p = get_closest_parent_drybones_dir(Path.cwd(), raise_if_none=True)
    return p / DIACRITICS_CONF_FILENAME


def get_char_to_alternatives_dict(fp=None) -> DiacriticDict:
    if fp is None:
        fp = get_diacritics_conf_fp()
    with open(fp, encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()]
    header_str = "char base options"
    assert lines[0] == header_str
    tups = [l.split(" ") for l in lines[1:]]
    diacritics_dict = DiacriticDict()
    for key, base, *alternatives in tups:
        key = translate_unicode_escapes_in_string(key)
        base = translate_unicode_escapes_in_string(base)
        alternatives = [translate_unicode_escapes_in_string(x) for x in alternatives]
        diacritics_dict.add(key, base, alternatives)
    return diacritics_dict


def translate_unicode_escapes_in_string(s: str) -> str:
    # s.encode("utf-8").decode("unicode-escape") will break any existing unicode chars in the string that are NOT in \uxxxx form
    # so use it only on the \uxxxx portions and don't modify any other part of the string
    pattern = r"\\u[0-9a-f]{4}"
    matches = re.finditer(pattern, s)
    spans = [m.span() for m in matches]

    res = ""
    next_index_to_get = 0
    for a, b in spans:
        if next_index_to_get < a:
            before_chunk = s[next_index_to_get:a]
            res += before_chunk

        chunk_orig = s[a:b]
        chunk_decoded = chunk_orig.encode("utf-8").decode("unicode-escape")
        res += chunk_decoded
        next_index_to_get = b
    # make sure you have the end of the string too
    if next_index_to_get < len(s):
        final_chunk = s[next_index_to_get:]
        res += final_chunk

    return res


def translate_diacritic_alternatives_in_string(s: str, d: DiacriticDict, to_base:bool=False, print_callback=None) -> str:
    if print_callback is None:
        print_callback = nop

    orig = s
    for k, base, alternatives in d.items():
        if to_base:
            target = base
            s = s.replace(k, base)
        else:
            target = k
        for a in alternatives:
            new_s = s.replace(a, target)
            if new_s != s:
                print_callback(f"{k = !r}: {s} --> {new_s}")
            s = new_s
    print_callback(f"outcome: {orig!r} --> {s!r}")  # debug
    return s



if __name__ == "__main__":
    test_strs = [
        "quốc ngữ asdf",  # should remain unmodified
        "qu\\u1ed1c ng\\u1eef asdf",  # should output correct Vietnamese chars as single chars
        "qu\\u00f4\\u0301c ng\\u01b0\\u0303 asdf",  # should output correct Vietnamese chars as vowels with quality diacritic in single char plus combining diacritics for tone
        "quo\\u0302\\u0301c ngu\\u031b\\u0303 asdf",  # should output correct Vietnamese chars as vowels with combining diacritics for both quality and tone
    ]

    for s in test_strs:
        print(translate_unicode_escapes_in_string(s))

