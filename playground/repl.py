from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict


# TODO load known parses and glosses from the corpus
known_parses_by_word = defaultdict(Counter)
known_glosses_by_morpheme = defaultdict(Counter)


def get_morphemes_from_user(word):
    print("word:", word)
    n_parses_to_show = 5
    ordered_suggested_parses = get_ordered_suggested_parses(word, n=n_parses_to_show)
    show_ordered_suggestions(ordered_suggested_parses, n=n_parses_to_show, 
                             string_if_no_options="no parses known for this word",
                             string_if_options="top parse candidates:",
    )
    parse = input("morphemes: ")
    # TODO if there are dashes used in the orthography and the user wants them in the morpheme form, can escape with backslash
    try:
        i = int(parse)
        parse = ordered_suggested_parses[i-1]  # because they are shown to user starting from 1
    except ValueError:
        pass
    print()
    return parse


def get_gloss_from_user(morpheme):
    print("morpheme:", morpheme)
    ordered_suggested_glosses = get_ordered_suggested_glosses(morpheme)
    n_glosses_to_show = 5
    show_ordered_suggestions(ordered_suggested_glosses, n=n_glosses_to_show,
                             string_if_no_options="no glosses known for this morpheme",
                             string_if_options="top gloss candidates:",
    )
    gloss = input("gloss: ")
    try:
        i = int(gloss)
        gloss = ordered_suggested_glosses[i-1]  # because they are shown to user starting from 1
    except ValueError:
        pass
    print()
    return gloss


def get_ordered_suggested_parses(word: str, n: int=None) -> List[str]:
    possible_parses = known_parses_by_word[word]
    lst = [k for k,v in sorted(possible_parses.items(), key=lambda kv: kv[-1], reverse=True)]
    if n is not None:
        return lst[:n]
    else:
        return lst


def get_ordered_suggested_glosses(morpheme: str, n: int=None) -> List[str]:
    possible_glosses = known_glosses_by_morpheme[morpheme]
    lst = [k for k,v in sorted(possible_glosses.items(), key=lambda kv: kv[-1], reverse=True)]
    if n is not None:
        return lst[:n]
    else:
        return lst


def show_ordered_suggestions(ordered_suggestions, n=5, string_if_no_options=None, string_if_options=None):
    if string_if_no_options is None:
        string_if_no_options = "no suggestions found"
    if len(ordered_suggestions) == 0:
        print(string_if_no_options)
    else:
        print(string_if_options)
        n = min(n, len(ordered_suggestions))
        for i in range(n):
            print(f"{i+1}. {ordered_suggestions[i]}")


def get_lines_from_text_file(text_file: Path) -> List[Dict]:
    lines = []
    with open(text_file) as f:
        contents = f.read()
    line_groups = contents.split("\n\n")
    for line_group in line_groups:
        rows = line_group.split("\n")
        row_by_label = {}
        for row in rows:
            if row == "":
                continue
            label, row_text = row.split(": ")
            assert label not in row_by_label
            row_by_label[label] = row_text
        lines.append(row_by_label)
    return lines


if __name__ == "__main__":
    text_file = Path.cwd() / "ProtoConticExampleSentences.txt"
    lines = get_lines_from_text_file(text_file)

    for line in lines:
        print(line)
        print(f"{line['N']}. {line['Bl']}")
        print(line["Tr"])
        print()

        words = line["Bl"].split()
        for word in words:
            parse = get_morphemes_from_user(word)
            known_parses_by_word[word][parse] += 1
            for morpheme in parse.split("-"):
                gloss = get_gloss_from_user(morpheme)
                known_glosses_by_morpheme[morpheme][gloss] += 1
    