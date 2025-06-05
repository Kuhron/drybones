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
from drybones.FileEditingUtil import setup_file_editing_operation, finish_file_editing_operation
from drybones.Line import Line
from drybones.Parse import Parse
from drybones.ReadingUtil import get_lines_from_all_drybones_files_in_dir
from drybones.Row import Row
from drybones.RowLabel import RowLabel, DEFAULT_LINE_DESIGNATION_LABEL, DEFAULT_ROW_LABELS_BY_STRING, DEFAULT_BASELINE_LABEL, DEFAULT_TRANSLATION_LABEL, DEFAULT_PARSE_LABEL, DEFAULT_GLOSS_LABEL, DEFAULT_PRODUCTION_LABEL, DEFAULT_JUDGMENT_LABEL
from drybones.WordAnalysis import WordAnalysis


# feature requests/ideas past v0.0.1 (not necessary right now, and I should focus now on parsing as much as I can with the existing features and not go back into development mode for a while)
# TODO get it to ignore inline comments like <S1:> for parsing/glossing, but keep them around in the strings (and also put them in the corresponding place in the parse/gloss)
# TODO figure out if/how I want to implement morphemes as sets of allomorphs, e.g. connecting "sah" to "sa/saV" (the initial of the LVC "sah-i- / sa-hi-" depending on analysis)
# TODO find where a certain gloss/parse/analysis comes from
# TODO edit an already-parsed line
# TODO mass reassign one analysis to another
# TODO when creating a new parse, show analyses' gloss sets that match it (often happens that, when the baseline has diacritic differences from wherever the analysis is connected to, you want the same parse/gloss for a different form)
# TODO implement diacritic-free matching of baseline strings (but keep the resulting suggestions as lower-priority than those that match the diacritics, could even do this based on the number of diacritic differences so you have a good ranking)
# TODO move the ReplaceAccents.py code into a DryBones command
# TODO show concordances of a word form, morpheme form, or gloss
# TODO once I have more than one file worked on in DryBones, draw the known values from all of them
# TODO maybe starting commands with a simpler key would be better, such as '/' or '\', since ':' requires also pressing shift
# TODO command during analysis choice dialogue: "/f {number}" to search for where that analysis is used
# TODO show some indication of acceptability for glosses/parses/analyses, since some are only used in unacceptable sentences, so I know the word doesn't actually mean that (although caveat that it could be unacceptable for some other reason in the sentence)
# could do better prediction of most likely glosses? e.g. based on the preceding morpheme; but this would be for way later and would probably introduce performance problems, don't do anything fancy right now, keep it simple or else it shouldn't be called DryBones (since you came up with that based on the phrase "bare-bones")
# TODO show line's parse/gloss in progress as the user chooses each thing (like how it's shown at the end once you've parsed the whole line, but want this at each stage so I can check easily what I just told it without scrolling up too much)
# TODO show tags, search by tags
# TODO highlight currently selected option when user types a number
# TODO allow use of arrow up/down to choose options
# TODO do we want to clear the screen at each step in the parsing? so that certain things appear in the same place to the eyes? (e.g. first option, the sentence itself) could reduce amount of eye-scanning needed for parseng. this could be a flag passed to the command to allow user preference


@click.command
@click.argument("text_fp", required=True, type=Path)
@click.argument("line_designation", required=False, type=str)
@click.option("--shuffle", "-s", type=bool, default=False, help="Shuffle the lines during parsing.")
@click.option("--overwrite", "-w", type=bool, default=False, help="Overwrite the input file. If false, a separate file will be created.")
@click.pass_context
def parse(ctx, text_fp, line_designation, shuffle, overwrite):
    """Parse text contents."""
    new_text_fp, lines, residues_by_location, line_designations_in_order, new_lines_by_designation = setup_file_editing_operation(text_fp, overwrite)

    if line_designation is not None:
        try:
            lines_to_parse = [new_lines_by_designation[line_designation]]
        except KeyError:
            click.echo(f"No line with designation {line_designation!r} was found.", err=True)
            return
    else:
        lines_to_parse = lines
    
    if shuffle:
        random.shuffle(lines_to_parse)
    
    lines_to_parse = [line for line in lines_to_parse if line.has_baseline() and not line.is_parsed_and_glossed()]

    lines_from_all_files = get_lines_from_all_drybones_files_in_dir(text_fp.parent)
    known_analyses_by_word = get_known_analyses(lines_from_all_files)
    known_parses_by_word = get_known_parses(known_analyses_by_word)
    known_glosses_by_morpheme = get_known_glosses(known_analyses_by_word)

    orthography_case_sensitive = False  # does anyone in their right mind do this? only Klingon, I think
    # but I could see it being used for things like restricting the text to ASCII / avoiding diacritics
    #     for the purposes of typing things up easily

    if len(lines_to_parse) == 0:
        if line_designation is not None:
            # user asked for a specific line, tell them what happened
            click.echo(f"Line {line_designation} is already parsed and glossed.")
        else:
            click.echo("This file is already completely parsed and glossed.")
    else:
        try:
            for line in lines_to_parse:
                known_analyses_by_word, known_parses_by_word, known_glosses_by_morpheme, new_lines_by_designation = parse_single_line(line, known_analyses_by_word, known_parses_by_word, known_glosses_by_morpheme, new_lines_by_designation)
        except KeyboardInterrupt:
            click.echo("\nQuitting parsing")
        finally:
            finish_file_editing_operation(new_text_fp, residues_by_location, line_designations_in_order, new_lines_by_designation)

    # TODO commands to implement when reading user input (no matter what input we are expecting, if we get a command then go do that instead)
    # :b = go back
    # :{designation} = go re-parse line of this designation
    # :q = quit


UNKNOWN_GLOSS = "?"
MORPHEME_DELIMITER = Cell.INTRA_CELL_DELIMITER
WORD_DELIMITER = Row.INTRA_ROW_DELIMITER
COMMAND_CHAR = ":"

RED = lambda s: Fore.RED + s + Style.RESET_ALL
GREEN = lambda s: Fore.GREEN + s + Style.RESET_ALL
YELLOW = lambda s: Fore.YELLOW + s + Style.RESET_ALL
RED_BACK = lambda s: Back.RED+Fore.BLACK + s + Style.RESET_ALL
GREEN_BACK = lambda s: Back.GREEN+Fore.BLACK + s + Style.RESET_ALL
YELLOW_BACK = lambda s: Back.YELLOW+Fore.BLACK + s + Style.RESET_ALL


def parse_single_line(line: Line, known_analyses_by_word: dict, known_parses_by_word: dict, known_glosses_by_morpheme: dict, new_lines_by_designation: dict):
    designation = line.designation

    baseline_row = line[DEFAULT_BASELINE_LABEL]
    translation_row = line[DEFAULT_TRANSLATION_LABEL]
    if translation_row is None:
        click.echo(f"No translation found in line:\n{line}")
        raise click.Abort()
    
    baseline_str = baseline_row.to_str(with_label=False)
    translation_str = translation_row.to_str()

    production_row = line[DEFAULT_PRODUCTION_LABEL]
    production_str = production_row.to_str(with_label=False) if production_row is not None else ""
    judgment_row = line[DEFAULT_JUDGMENT_LABEL]
    judgment_str = judgment_row.to_str(with_label=False) if judgment_row is not None else ""

    print_baseline(designation, baseline_str, production_str, judgment_str)
    click.echo(translation_str + "\n")

    new_rows = [row for row in line.rows]

    # TODO update workflow to include word analysis
    # first show user existing analyses and ask if they want one of those
    # if not, show existing parses and ask if they want one of those
    # given whatever parse they chose/made, do the normal flow of glossing each morpheme

    words = [cell.to_str() for cell in baseline_row.cells]
    parse_cells = []
    gloss_cells = []
    for i, word in enumerate(words):
        print_baseline(designation, baseline_str, production_str, judgment_str, words=words, word_index_to_highlight=i)
        click.echo(translation_str)
        word = get_word_key_from_baseline_word(word)

        if word not in known_analyses_by_word:
            analysis = None
        else:
            analysis = get_analysis_from_user(word, known_analyses_by_word)

        if analysis is not None:
            parse = analysis.parse
            glosses = analysis.glosses
            parse_cell = Cell(strs=parse.morpheme_strs)
            gloss_cell = Cell(strs=glosses)
            accepted_analysis = analysis
        else:
            parse = get_parse_from_user(word, known_parses_by_word)
            known_parses_by_word[word][parse] += 1
            glosses_this_word = []
            morpheme_strs = parse.morpheme_strs
            for j, morpheme in enumerate(morpheme_strs):
                print_baseline(designation, baseline_str, production_str, judgment_str, words=words, word_index_to_highlight=i, morphemes=morpheme_strs, morpheme_index_to_highlight=j)
                click.echo(translation_str)
                gloss_str = get_gloss_from_user(morpheme, known_glosses_by_morpheme)
                known_glosses_by_morpheme[morpheme][gloss_str] += 1
                glosses_this_word.append(gloss_str)
            accepted_analysis = WordAnalysis(parse, glosses_this_word)
            parse_cell = Cell(strs=morpheme_strs)
            gloss_cell = Cell(strs=glosses_this_word)
        
        known_analyses_by_word[word][accepted_analysis] += 1
        parse_cells.append(parse_cell)
        gloss_cells.append(gloss_cell)
    click.echo()

    parse_row = Row(DEFAULT_PARSE_LABEL, parse_cells)
    gloss_row = Row(DEFAULT_GLOSS_LABEL, gloss_cells)
    new_rows += [parse_row, gloss_row]

    new_line = Line(designation, new_rows)
    click.echo(f"new_line:\n{new_line.to_string_for_drybones_file()}\n")
    new_lines_by_designation[new_line.designation] = new_line
    
    return known_analyses_by_word, known_parses_by_word, known_glosses_by_morpheme, new_lines_by_designation


def remove_punctuation(word_str):
    # for purposes of identifying if we have a parse of this word
    res = word_str
    try:
        while any(res.endswith(x) for x in [".", ",", "?", "!", ";", ")", "\""]):
            res = res[:-1]
        while any(res.startswith(x) for x in ["(", "\""]):
            res = res[1:]
    except IndexError:
        click.echo(f"removing punctuation from {word_str!r} resulted in blank string", err=True)
        raise click.Abort()
    return res


def get_word_key_from_baseline_word(word):
    return remove_punctuation(word.lower())


def get_known_analyses(lines):
    known_analyses_by_word = defaultdict(Counter)
    baseline_label = DEFAULT_BASELINE_LABEL
    parse_label = DEFAULT_PARSE_LABEL
    gloss_label = DEFAULT_GLOSS_LABEL
    for l in lines:
        baseline_row = l[baseline_label]
        parse_row = l[parse_label]
        gloss_row = l[gloss_label]
        has_baseline = baseline_row is not None
        has_parse = parse_row is not None
        has_gloss = gloss_row is not None
        if has_baseline:
            if has_parse and has_gloss:
                # normal case, construct the analysis
                for bl_cell, parse_cell, gloss_cell in zip(baseline_row, parse_row, gloss_row, strict=True):
                    bl_str = get_word_key_from_baseline_word(bl_cell.to_str())
                    morpheme_strs = parse_cell.strs
                    parse = Parse(morpheme_strs)
                    glosses = gloss_cell.strs
                    analysis = WordAnalysis(parse, glosses)
                    known_analyses_by_word[bl_str][analysis] += 1
            elif has_parse or has_gloss:
                click.echo(f"line is parsed or glossed but not both:\n{l}")
                raise click.Abort()
            else:
                # it has a baseline but neither parse nor gloss, ignore it, it's not done yet
                continue
        else:
            if has_parse or has_gloss:
                click.echo(f"line has no baseline but has parse and/or gloss:\n{l}")
                raise click.Abort()
            else:
                # it has none of the above, ignore it
                continue
    
    return known_analyses_by_word


def get_known_parses(known_analyses_by_word):
    known_parses_by_word = defaultdict(Counter)

    for word, analysis_counter in known_analyses_by_word.items():
        for analysis, count in analysis_counter.items():
            parse = analysis.parse
            known_parses_by_word[word][parse] += count
    
    return known_parses_by_word


def get_known_glosses(known_analyses_by_word):
    known_glosses_by_morpheme = defaultdict(Counter)

    for word, analysis_counter in known_analyses_by_word.items():
        for analysis, count in analysis_counter.items():
            parse = analysis.parse
            morpheme_strs = parse.morpheme_strs
            glosses = analysis.glosses
            for morpheme_str, gloss in zip(morpheme_strs, glosses, strict=True):
                known_glosses_by_morpheme[morpheme_str][gloss] += count

    return known_glosses_by_morpheme


def get_analysis_from_user(word, known_analyses_by_word) -> WordAnalysis:
    click.echo(f"word: {word}")
    n_analyses_to_show = 15
    ordered_suggested_analyses = get_ordered_suggestions(key=word, known_dict=known_analyses_by_word, n=n_analyses_to_show)
    show_ordered_suggestions(ordered_suggested_analyses, n=n_analyses_to_show, display_func=lambda a: a.str,
                             string_if_no_options="no analyses known for this word",
                             string_if_options="top analysis candidates:",
    )
    while True:
        inp = input("choose existing analysis, or press enter to create a new one: ")
        if inp == "":
            analysis = None
            break
        try:
            i = int(inp)
            analysis = ordered_suggested_analyses[i-1]
            break
        except ValueError:
            click.echo("invalid input")
        except IndexError:
            click.echo("that number is out of range")
    click.echo()
    return analysis


def get_parse_from_user(word, known_parses_by_word) -> Parse:
    click.echo(f"word: {word}")
    n_parses_to_show = 15
    ordered_suggested_parses = get_ordered_suggestions(key=word, known_dict=known_parses_by_word, n=n_parses_to_show)
    show_ordered_suggestions(ordered_suggested_parses, n=n_parses_to_show, display_func=lambda p: p.str, 
                             string_if_no_options="no parses known for this word",
                             string_if_options="top parse candidates:",
    )
    while True:
        inp = input("morphemes: ")
        try:
            i = int(inp)
            parse = ordered_suggested_parses[i-1]  # because they are shown to user starting from 1
            break
        except ValueError:
            parse_str = inp if inp != "" else word

            if Row.INTRA_ROW_DELIMITER in parse_str:
                click.echo(f"the character {Row.INTRA_ROW_DELIMITER!r} is not allowed in the parse of an individual word")
                return get_parse_from_user(word, known_parses_by_word)
    
            morpheme_strs = parse_str.split(MORPHEME_DELIMITER)
            parse = Parse(morpheme_strs)
            break
        except IndexError:
            click.echo("that number is out of range")
    click.echo()
    return parse


def get_gloss_from_user(morpheme, known_glosses_by_morpheme):
    click.echo(f"morpheme: {morpheme}")
    n_glosses_to_show = 15
    ordered_suggested_glosses = get_ordered_suggestions(key=morpheme, known_dict=known_glosses_by_morpheme, n=n_glosses_to_show)
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
        click.echo("that number is out of range")
        return get_gloss_from_user(morpheme, known_glosses_by_morpheme)
    click.echo()

    if Cell.INTRA_CELL_DELIMITER in gloss:
        click.echo(f"the character {Cell.INTRA_CELL_DELIMITER!r} is not allowed in the gloss of an individual morpheme")
        return get_gloss_from_user(morpheme, known_glosses_by_morpheme)
    elif Row.INTRA_ROW_DELIMITER in gloss:
        click.echo(f"the character {Row.INTRA_ROW_DELIMITER!r} is not allowed in the gloss of an individual morpheme")
        return get_gloss_from_user(morpheme, known_glosses_by_morpheme)

    if gloss == "":
        gloss = UNKNOWN_GLOSS
    return gloss


def get_ordered_suggestions(key, known_dict, n: int=None):
    possibles = known_dict[key]
    lst = [k for k,v in sorted(possibles.items(), key=lambda kv: kv[-1], reverse=True)]
    if n is not None:
        return lst[:n]
    else:
        return lst


def show_ordered_suggestions(ordered_suggestions, n=5, display_func=None, string_if_no_options=None, string_if_options=None) -> None:
    if display_func is None:
        display_func = lambda x: x
    if string_if_no_options is None:
        string_if_no_options = "no suggestions found"
    if len(ordered_suggestions) == 0:
        click.echo(string_if_no_options)
    else:
        click.echo(string_if_options)
        n = min(n, len(ordered_suggestions))
        for i in range(n):
            s = display_func(ordered_suggestions[i])
            click.echo(f"{i+1}. {s}")


def print_baseline(designation, baseline_text, production_str, judgment_str, words=None, word_index_to_highlight=None, morphemes=None, morpheme_index_to_highlight=None) -> None:
    highlight_word = word_index_to_highlight is not None
    highlight_morpheme = morpheme_index_to_highlight is not None
    if highlight_word and highlight_morpheme:
        before_words = words[:word_index_to_highlight]
        after_words = words[word_index_to_highlight+1:]
        morpheme_strs = [YELLOW(x) if i == morpheme_index_to_highlight else GREEN(x) for i,x in enumerate(morphemes)]
        word_str = Cell.INTRA_CELL_DELIMITER.join(morpheme_strs)
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
    
    pj_str = "" if production_str == "" and judgment_str == "" else production_str + judgment_str + " "
    click.echo(f"{designation}. {pj_str}{text}")


def is_command(s: str) -> bool:
    return s.startswith(COMMAND_CHAR)

