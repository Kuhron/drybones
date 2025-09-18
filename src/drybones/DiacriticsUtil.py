# functions about dealing with diacritics, converting between different representations of a character, matching regex while ignoring diacritics, etc.

import click
from pathlib import Path
from typing import List, Dict

from drybones.DiacriticDict import DiacriticDict
from drybones.ProjectUtil import get_closest_parent_drybones_dir


DIACRITICS_CONF_FILENAME = "diacritics.conf"


def get_diacritics_conf_fp():
    p = get_closest_parent_drybones_dir(Path.cwd(), raise_if_none=True)
    return p / DIACRITICS_CONF_FILENAME


def get_char_to_alternatives_dict() -> DiacriticDict:
    fp = get_diacritics_conf_fp()
    with open(fp) as f:
        lines = f.readlines()
    tups = [l.strip().split(" ") for l in lines]
    diacritics_dict = DiacriticDict()
    for key, base, *alternatives in tups:
        alternatives = [translate_unicode_escapes_in_string(x) for x in alternatives]
        diacritics_dict.add(key, base, alternatives)
    return diacritics_dict


def translate_unicode_escapes_in_string(s: str) -> str:
    # https://www.reddit.com/r/learnpython/comments/fi7p9y/replacing_literal_u_in_string_with_corresponding/
    return s.encode("utf-8").decode("unicode-escape")


def translate_diacritic_alternatives_in_string(s: str, d: DiacriticDict, to_base:bool=False) -> str:
    orig = s
    for k, base, alternatives in d.items():
        if to_base:
            target = base
            s = s.replace(k, base)
        else:
            target = k
        for a in alternatives:
            s = s.replace(a, target)
    # print(f"{orig!r} -> {s!r}")  # debug
    return s

