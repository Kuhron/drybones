# for holding information about diacritics/diacritic-marked chars, and strings that they are treated as equivalent to


from typing import List


class DiacriticCharacter:
    def __init__(self, char: str, base: str, alternatives: List[str]):
        self.char = char
        self.base = base
        self.alternatives = alternatives

    def __repr__(self):
        alt_str = ", ".join(f"{x!r}" for x in self.alternatives)
        return f"<DiacriticCharacter {self.char!r} (base {self.base!r}): {alt_str}>"


class DiacriticDict:
    def __init__(self):
        self.dct = {}

    def add(self, char: str, base: str, alternatives: List[str]):
        c = DiacriticCharacter(char, base, alternatives)
        self.dct[char] = c

    def items(self):
        for char, dc in self.dct.items():
            yield char, dc.base, dc.alternatives

    def __repr__(self):
        s = "<DiacriticDict {\n"
        for char, diacritic_char in sorted(self.dct.items()):
            s += f"  {char}: {diacritic_char},\n"
        s += "}"
        return s
