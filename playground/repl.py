import random
from collections import Counter, defaultdict, OrderedDict
from pathlib import Path
from typing import List, Dict

# terminal color printing
from colorama import init as colorama_init
from colorama import Fore, Back, Style
colorama_init()


# TODO load known parses and glosses from the corpus
known_parses_by_word = defaultdict(Counter)
known_glosses_by_morpheme = defaultdict(Counter)

UNKNOWN_GLOSS = "?"
MORPHEME_DELIMITER = "-"
WORD_DELIMITER = " "
COMMAND_CHAR = ":"

RED = lambda s: Fore.RED + s + Style.RESET_ALL
GREEN = lambda s: Fore.GREEN + s + Style.RESET_ALL
YELLOW = lambda s: Fore.YELLOW + s + Style.RESET_ALL
RED_BACK = lambda s: Back.RED+Fore.BLACK + s + Style.RESET_ALL
GREEN_BACK = lambda s: Back.GREEN+Fore.BLACK + s + Style.RESET_ALL
YELLOW_BACK = lambda s: Back.YELLOW+Fore.BLACK + s + Style.RESET_ALL


def get_morphemes_from_user(word):
    print("word:", word)
    n_parses_to_show = 5
    ordered_suggested_parses = get_ordered_suggested_parses(word, n=n_parses_to_show)
    show_ordered_suggestions(ordered_suggested_parses, n=n_parses_to_show, 
                             string_if_no_options="no parses known for this word",
                             string_if_options="top parse candidates:",
    )
    inp = input("morphemes: ")
    # TODO if there are dashes used in the orthography and the user wants them in the morpheme form, can escape with backslash
    try:
        i = int(inp)
        parse_str = ordered_suggested_parses[i-1]  # because they are shown to user starting from 1
    except ValueError:
        parse_str = inp
    except IndexError:
        print("oops, that number is out of range")
        return get_morphemes_from_user(word)
    print()

    if inp == "":
        parse_str = word
    return parse_str.split(MORPHEME_DELIMITER)


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
        pass  # use whatever user gave for the gloss
    except IndexError:
        print("oops, that number is out of range")
        return get_gloss_from_user(morpheme)
    print()

    if gloss == "":
        gloss = UNKNOWN_GLOSS
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


def show_ordered_suggestions(ordered_suggestions, n=5, string_if_no_options=None, string_if_options=None) -> None:
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
        row_by_label = OrderedDict()
        for row in rows:
            if row == "":
                continue
            label, row_text = row.split(": ")
            assert label not in row_by_label
            row_by_label[label] = row_text
        lines.append(row_by_label)
    return lines


def print_baseline(number, baseline_text, words=None, word_index_to_highlight=None, morphemes=None, morpheme_index_to_highlight=None) -> None:
    highlight_word = word_index_to_highlight is not None
    highlight_morpheme = morpheme_index_to_highlight is not None
    if highlight_word and highlight_morpheme:
        before_words = words[:word_index_to_highlight]
        after_words = words[word_index_to_highlight+1:]
        morpheme_strs = [RED(x) if i == morpheme_index_to_highlight else GREEN(x) for i,x in enumerate(morphemes)]
        word_str = "".join(morpheme_strs)
        word_strs = before_words + [word_str] + after_words
        text = WORD_DELIMITER.join(word_strs)
    elif highlight_word and not highlight_morpheme:
        before_words = words[:word_index_to_highlight]
        after_words = words[word_index_to_highlight+1:]
        word = words[word_index_to_highlight]
        word_str = GREEN(word)
        word_strs = before_words + [word_str] + after_words
        text = WORD_DELIMITER.join(word_strs)
    elif not highlight_word and highlight_morpheme:
        raise ValueError("shouldn't be highlighting a morpheme without highlighting a word")
    else:
        text = baseline_text
    
    print(f"{number}. {text}")


def is_command(s: str) -> bool:
    return s.startswith(COMMAND_CHAR)



if __name__ == "__main__":
    text_file = Path.cwd() / "ProtoConticExampleSentences.txt"

    number_label = "N"
    baseline_label = "Baseline"
    parse_label = "Parse"
    morpheme_gloss_label = "Gloss"
    morpheme_class_label = "Class"
    word_gloss_label = "Wordgloss"
    word_class_label = "Wordclass"
    translation_label = "Translation"

    labels = [
        number_label,
        parse_label,
        morpheme_gloss_label,
        morpheme_class_label,
        word_gloss_label,
        word_class_label,
        translation_label,
    ]

    lines = get_lines_from_text_file(text_file)
    random.shuffle(lines)

    # TODO config for if the orthography is case-sensitive
    # by default assume not case-sensitive, so set everything in baseline to lowercase
    orthography_case_sensitive = False

    for line in lines:
        number = line[number_label]
        baseline_text = line[baseline_label]
        words = baseline_text.split()
        translation = line[translation_label]

        print_baseline(number, baseline_text)
        print(translation)
        print()

        for i, word in enumerate(words):
            print_baseline(number, baseline_text, words, i)
            print(translation)
            if orthography_case_sensitive:
                raise ValueError("can't handle case-sensitive orthographies yet")
            else:
                word = word.lower()
            morphemes = get_morphemes_from_user(word)
            parse = MORPHEME_DELIMITER.join(morphemes)
            known_parses_by_word[word][parse] += 1
            glosses_this_word = []
            for j, morpheme in enumerate(morphemes):
                print_baseline(number, baseline_text, words, i, morphemes, j)
                print(translation)
                gloss = get_gloss_from_user(morpheme)
                known_glosses_by_morpheme[morpheme][gloss] += 1
                glosses_this_word.append(gloss)
            print("received glosses:", MORPHEME_DELIMITER.join(glosses_this_word))
            print()
        print()

    # TODO print the edited line with rows in order, to some output file that could then [replace / be merged with] the input to update it
    # don't enforce the input being in a certain row order, but could just copy the orders we've seen in the input file
    
    # TODO commands to implement when reading user input (no matter what input we are expecting, if we get a command then go do that instead)
    # :b = go back
    # :{number} = go re-parse line of this number
    # :q = quit
