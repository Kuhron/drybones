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
from drybones.RowLabel import RowLabel, DEFAULT_LINE_NUMBER_LABEL, DEFAULT_ROW_LABELS_BY_STRING, DEFAULT_BASELINE_LABEL, DEFAULT_TRANSLATION_LABEL, DEFAULT_PARSE_LABEL, DEFAULT_GLOSS_LABEL


# TODO get it to ignore inline comments like <S1:> for parsing/glossing, but keep them around in the strings (and also put them in the corresponding place in the parse/gloss)
# TODO get underscores working for the aligned lines, like how "musu maisa" has a space in the baseline but is treated as one unit for parse/gloss, parsed as "musu_maisa"


@click.command
@click.argument("text_fp", required=True, type=Path)
@click.argument("line_number", required=False, type=int)
@click.pass_context
def parse(ctx, text_fp: Path, line_number: int=None):
    """Parse text contents."""
    lines, residues_by_location = get_lines_from_text_file(text_fp)
    random.shuffle(lines)

    new_lines_by_number = {l.number: l for l in lines}

    known_parses_by_word = get_known_parses(lines)
    known_glosses_by_morpheme = get_known_glosses(lines)

    # TODO config for if the orthography is case-sensitive
    # by default assume not case-sensitive, so set everything in baseline to lowercase
    orthography_case_sensitive = False

    try:
        for line in lines:
            if line.is_parsed_and_glossed():
                continue
            number = line.number
            baseline_row = line[DEFAULT_BASELINE_LABEL]
            translation_row = line[DEFAULT_TRANSLATION_LABEL]
            baseline_str = baseline_row.to_str()
            translation_str = translation_row.to_str()

            print_baseline(number, baseline_str)
            click.echo(translation_str + "\n")

            new_rows = [row for row in line.rows]

            words = [cell.to_str() for cell in baseline_row.cells]
            parse_cells = []
            gloss_cells = []
            for i, word in enumerate(words):
                print_baseline(number, baseline_str, words, i)
                click.echo(translation_str)
                if orthography_case_sensitive:
                    raise ValueError("can't handle case-sensitive orthographies yet")
                else:
                    word = remove_punctuation(word.lower())
                morphemes = get_morphemes_from_user(word, known_parses_by_word)
                parse_str = MORPHEME_DELIMITER.join(morphemes)
                known_parses_by_word[word][parse_str] += 1
                glosses_this_word = []
                for j, morpheme in enumerate(morphemes):
                    print_baseline(number, baseline_str, words, i, morphemes, j)
                    click.echo(translation_str)
                    gloss_str = get_gloss_from_user(morpheme, known_glosses_by_morpheme)
                    known_glosses_by_morpheme[morpheme][gloss_str] += 1
                    glosses_this_word.append(gloss_str)

                parse_cell = Cell(strs=morphemes)
                parse_cells.append(parse_cell)
                gloss_cell = Cell(strs=glosses_this_word)
                gloss_cells.append(gloss_cell)
            click.echo()

            parse_row = Row(DEFAULT_PARSE_LABEL, parse_cells)
            gloss_row = Row(DEFAULT_GLOSS_LABEL, gloss_cells)
            new_rows += [parse_row, gloss_row]

            new_line = Line(number, new_rows)
            click.echo(f"new_line:\n{new_line.to_string_for_text_file()}\n")
            new_lines_by_number[new_line.designation] = new_line
    except KeyboardInterrupt:
        click.echo("\nQuitting parsing")
    finally:
        # construct the output string to replace the input file's contents
        # TODO put this in its own function
        new_lines = [v for k,v in sorted(new_lines_by_number.items())]
        s_to_write = ""
        locations_checked = set()
        for i, l in enumerate(new_lines):
            location = i-0.5
            locations_checked.add(location)
            residue_before_line = residues_by_location.get(location, "")
            line_str = l.to_string_for_text_file() 
            s_to_write += residue_before_line + line_str
        final_location = i+0.5  # actually using the final value of a loop variable outside the loop? crazy
        locations_checked.add(final_location)
        residue_at_end = residues_by_location.get(final_location, "")
        s_to_write += residue_at_end
        assert set(residues_by_location.keys()) - locations_checked == set(), "failed to check for residues at some locations"
        with open(text_fp, "w") as f:
            f.write(s_to_write)

    # TODO print the edited line with rows in order, to some output file that could then [replace / be merged with] the input to update it
    # don't enforce the input being in a certain row order, but could just copy the orders we've seen in the input file

    # TODO commands to implement when reading user input (no matter what input we are expecting, if we get a command then go do that instead)
    # :b = go back
    # :{number} = go re-parse line of this number
    # :q = quit


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


def remove_punctuation(word_str):
    # for purposes of identifying if we have a parse of this word
    if any(word_str.endswith(x) for x in [".", ",", "?", "!", ";"]):
        return word_str[:-1]
    return word_str


def get_known_parses(lines):
    known_parses_by_word = defaultdict(Counter)
    baseline_label = DEFAULT_BASELINE_LABEL
    parse_label = DEFAULT_PARSE_LABEL
    for l in lines:
        baseline_row = l[baseline_label]
        parse_row = l[parse_label]
        if parse_row is not None:
            for bl_cell, parse_cell in zip(baseline_row, parse_row, strict=True):
                bl_str = remove_punctuation(bl_cell.to_str())
                parse_str = parse_cell.to_str()
                known_parses_by_word[bl_str][parse_str] += 1
    
    return known_parses_by_word


def get_known_glosses(lines):
    known_glosses_by_morpheme = defaultdict(Counter)
    parse_label = DEFAULT_PARSE_LABEL
    gloss_label = DEFAULT_GLOSS_LABEL
    for l in lines:
        parse_row = l[parse_label]
        gloss_row = l[gloss_label]
        if gloss_row is not None:
            for parse_cell, gloss_cell in zip(parse_row, gloss_row, strict=True):
                for parse_str, gloss_str in zip(parse_cell.strs, gloss_cell.strs, strict=True):
                    known_glosses_by_morpheme[parse_str][gloss_str] += 1
    
    return known_glosses_by_morpheme


def get_morphemes_from_user(word, known_parses_by_word):
    click.echo(f"word: {word}")
    n_parses_to_show = 5
    ordered_suggested_parses = get_ordered_suggested_parses(word, known_parses_by_word, n=n_parses_to_show)
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
        return get_morphemes_from_user(word, known_parses_by_word)
    click.echo()

    if inp == "":
        parse_str = word
    return parse_str.split(MORPHEME_DELIMITER)


def get_gloss_from_user(morpheme, known_glosses_by_morpheme):
    click.echo(f"morpheme: {morpheme}")
    n_glosses_to_show = 5
    ordered_suggested_glosses = get_ordered_suggested_glosses(morpheme, known_glosses_by_morpheme, n=n_glosses_to_show)
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
        return get_gloss_from_user(morpheme, known_glosses_by_morpheme)
    click.echo()

    if Cell.INTRA_CELL_DELIMITER in gloss:
        click.echo(f"the character {Cell.INTRA_CELL_DELIMITER!r} is not allowed in the gloss of an individual morpheme")
        return get_gloss_from_user(morpheme, known_glosses_by_morpheme)

    if gloss == "":
        gloss = UNKNOWN_GLOSS
    return gloss


def get_ordered_suggested_parses(word: str, known_parses_by_word, n: int=None) -> List[str]:
    possible_parses = known_parses_by_word[word]
    lst = [k for k,v in sorted(possible_parses.items(), key=lambda kv: kv[-1], reverse=True)]
    if n is not None:
        return lst[:n]
    else:
        return lst


def get_ordered_suggested_glosses(morpheme: str, known_glosses_by_morpheme, n: int=None) -> List[str]:
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


def get_lines_from_text_file(text_file: Path):
    line_groups, residues_by_location = get_line_group_strings_from_text_file(text_file)
    lines = []
    row_labels_by_string = {k:v for k,v in DEFAULT_ROW_LABELS_BY_STRING.items()}
    for line_group in line_groups:
        line_number = None
        row_strs = line_group.split("\n")
        rows = []
        row_length = None
        for row_str in row_strs:
            if row_str == "":
                continue
            label_str, *row_text_pieces = row_str.split(RowLabel.AFTER_LABEL_CHAR)
            if len(row_text_pieces) == 0:
                click.echo(f"row has no label:\n{row_str!r}\n")
                raise click.Abort()
            else:
                row_text = RowLabel.AFTER_LABEL_CHAR.join(row_text_pieces)
            
            row_text = row_text.strip()
            try:
                label = row_labels_by_string[label_str]
            except KeyError:
                label = RowLabel(label_str, aligned=False)
                row_labels_by_string[label_str] = label

            if label == DEFAULT_LINE_NUMBER_LABEL:
                line_number = row_text

            if label.is_aligned():
                cell_texts = row_text.split(Row.INTRA_ROW_DELIMITER)
                cells = []
                for cell_text in cell_texts:
                    cell = Cell(cell_text.split(Cell.INTRA_CELL_DELIMITER))
                    cells.append(cell)
                this_row_length = len(cells)
                if row_length is None:
                    row_length = this_row_length
                else:
                    assert this_row_length == row_length, f"expected row of length {row_length} but got {this_row_length}:\n{row_text}"
            else:
                cells = [Cell([row_text])]
            
            row = Row(label, cells)
            rows.append(row)
        line = Line(line_number, rows)
        lines.append(line)
    return lines, residues_by_location


def get_line_group_strings_from_text_file(text_file: Path):
    with open(text_file) as f:
        contents = f.read()
    l = contents.split(Line.BEFORE_LINE)
    groups = []
    residue_before_first_group = l[0]
    residues_by_location = {-0.5: residue_before_first_group}  # location is +/- 0.5 from group index (regardless of the group's labeled number)
    for s in l[1:]:
        group, *residues = s.split(Line.AFTER_LINE)  # there may be stray AFTER_LINE delimiters in the residue
        groups.append(group)
        if len(residues) > 0:
            residue = Line.AFTER_LINE.join(residues)
            if len(residue.strip()) > 0:
                click.echo(f"ignoring text outside of line block:\n{residue!r}\n")
            last_group_index = len(groups) - 1
            location = last_group_index + 0.5
            assert location not in residues_by_location
            residues_by_location[location] = residue
    # TODO make a LineGroupString object and ResidueString object for holding the original file contents after breaking it apart
    # then can call a function on a LineGroupString to parse it into a Line
    # but want the top-level parse command call to be able to just grab the original string for a group that was unedited, and for a residue, without me stripping off whitespace and then adding it back on (error prone)
    return groups, residues_by_location


def print_baseline(number, baseline_text, words=None, word_index_to_highlight=None, morphemes=None, morpheme_index_to_highlight=None) -> None:
    highlight_word = word_index_to_highlight is not None
    highlight_morpheme = morpheme_index_to_highlight is not None
    if highlight_word and highlight_morpheme:
        before_words = words[:word_index_to_highlight]
        after_words = words[word_index_to_highlight+1:]
        morpheme_strs = [YELLOW(x) if i == morpheme_index_to_highlight else GREEN(x) for i,x in enumerate(morphemes)]
        word_str = "".join(morpheme_strs)
        word_strs = before_words + [word_str] + after_words
        text = WORD_DELIMITER.join(word_strs)
    elif highlight_word and not highlight_morpheme:
        before_words = words[:word_index_to_highlight]
        after_words = words[word_index_to_highlight+1:]
        word = words[word_index_to_highlight]
        word_str = YELLOW(word)
        word_strs = before_words + [word_str] + after_words
        text = WORD_DELIMITER.join(word_strs)
    elif not highlight_word and highlight_morpheme:
        raise ValueError("shouldn't be highlighting a morpheme without highlighting a word")
    else:
        text = baseline_text
    
    click.echo(f"{number}. {text}")


def is_command(s: str) -> bool:
    return s.startswith(COMMAND_CHAR)

