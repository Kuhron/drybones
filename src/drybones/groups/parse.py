# things relating to parsing texts

import click
import random
from collections import Counter, defaultdict, OrderedDict
from pathlib import Path
from typing import List, Dict

# terminal color printing
from colorama import init as colorama_init
from colorama import Fore, Back, Style
colorama_init()

from drybones.Cell import Cell
from drybones.Line import Line
from drybones.Row import Row
from drybones.RowLabel import RowLabel, DEFAULT_LINE_NUMBER_LABEL, DEFAULT_ROW_LABELS_BY_STRING, DEFAULT_BASELINE_LABEL, DEFAULT_TRANSLATION_LABEL


@click.command
@click.argument("text_name")
@click.argument("line_number", required=False, type=int)
@click.pass_context
def parse(ctx, text_name, line_number):
    """Parse text contents."""
    text_file = Path("/home/kuhron/drybones/playground/ProtoConticExampleSentences.txt")

    lines = get_lines_from_text_file(text_file)
    random.shuffle(lines)

    # TODO config for if the orthography is case-sensitive
    # by default assume not case-sensitive, so set everything in baseline to lowercase
    orthography_case_sensitive = False

    for line in lines:
        number = line.number
        baseline_row = line[DEFAULT_BASELINE_LABEL]
        translation_row = line[DEFAULT_TRANSLATION_LABEL]
        baseline_str = baseline_row.to_str()
        translation_str = translation_row.to_str()

        print_baseline(number, baseline_str)
        click.echo(translation_str + "\n")

        words = [cell.to_str() for cell in baseline_row.cells]
        for i, word in enumerate(words):
            print_baseline(number, baseline_str, words, i)
            click.echo(translation_str)
            if orthography_case_sensitive:
                raise ValueError("can't handle case-sensitive orthographies yet")
            else:
                word = word.lower()
            morphemes = get_morphemes_from_user(word)
            parse = MORPHEME_DELIMITER.join(morphemes)
            known_parses_by_word[word][parse] += 1
            glosses_this_word = []
            for j, morpheme in enumerate(morphemes):
                print_baseline(number, baseline_str, words, i, morphemes, j)
                click.echo(translation_str)
                gloss = get_gloss_from_user(morpheme)
                known_glosses_by_morpheme[morpheme][gloss] += 1
                glosses_this_word.append(gloss)
            click.echo(f"received glosses: {MORPHEME_DELIMITER.join(glosses_this_word)}")
            click.echo()
        click.echo()

    # TODO print the edited line with rows in order, to some output file that could then [replace / be merged with] the input to update it
    # don't enforce the input being in a certain row order, but could just copy the orders we've seen in the input file
    
    # TODO commands to implement when reading user input (no matter what input we are expecting, if we get a command then go do that instead)
    # :b = go back
    # :{number} = go re-parse line of this number
    # :q = quit




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
    click.echo(f"word: {word}")
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
        click.echo("oops, that number is out of range")
        return get_morphemes_from_user(word)
    click.echo()

    if inp == "":
        parse_str = word
    return parse_str.split(MORPHEME_DELIMITER)


def get_gloss_from_user(morpheme):
    click.echo(f"morpheme: {morpheme}")
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
        click.echo("oops, that number is out of range")
        return get_gloss_from_user(morpheme)
    click.echo()

    if Cell.INTRA_CELL_DELIMITER in gloss:
        click.echo(f"the character {Cell.INTRA_CELL_DELIMITER!r} is not allowed in the gloss of an individual morpheme")
        return get_gloss_from_user(morpheme)

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
        click.echo(string_if_no_options)
    else:
        click.echo(string_if_options)
        n = min(n, len(ordered_suggestions))
        for i in range(n):
            click.echo(f"{i+1}. {ordered_suggestions[i]}")


def get_lines_from_text_file(text_file: Path) -> List[Line]:
    line_groups = get_line_group_strings_from_text_file(text_file)
    lines = []
    row_labels_by_string = {k:v for k,v in DEFAULT_ROW_LABELS_BY_STRING.items()}
    for line_group in line_groups:
        line_number = None
        row_strs = line_group.split("\n")
        rows = []
        for row_str in row_strs:
            if row_str == "":
                continue
            label_str, row_text = row_str.split(RowLabel.AFTER_LABEL_CHAR)
            row_text = row_text.strip()
            try:
                label = row_labels_by_string[label_str]
            except KeyError:
                label = RowLabel(label_str, aligned=False)
                row_labels_by_string[label_str] = label

            if label == DEFAULT_LINE_NUMBER_LABEL:
                line_number = int(row_text)

            if label.is_aligned():
                cell_texts = row_text.split(Row.INTRA_ROW_DELIMITER)
                cells = []
                for cell_text in cell_texts:
                    cell = Cell(cell_text.split(Cell.INTRA_CELL_DELIMITER))
                    cells.append(cell)
            else:
                cells = [Cell([row_text])]
            
            row = Row(label, cells)
            rows.append(row)
        line = Line(line_number, rows)
        lines.append(line)
    return lines


def get_line_group_strings_from_text_file(text_file: Path) -> List[str]:
    with open(text_file) as f:
        contents = f.read()
    l = contents.split(Line.BEFORE_LINE)
    groups = []
    for s in l:
        group, *residues = s.split(Line.AFTER_LINE)
        group = group.strip()
        if len(residues) > 0:
            residue = Line.AFTER_LINE.join(residues).strip()
            # throw the residue away
            if len(residue) > 0:
                click.echo(f"ignoring text outside of line block:\n{residue!r}\n")
        if len(group) > 0:
            groups.append(group)
    return groups


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
    
    click.echo(f"{number}. {text}")


def is_command(s: str) -> bool:
    return s.startswith(COMMAND_CHAR)

