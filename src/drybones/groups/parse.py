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

from drybones.AnalysisUtil import get_known_analyses, get_known_parses, get_known_glosses, get_analysis_from_user, get_parse_from_user, get_gloss_from_user, get_word_key_from_baseline_word
from drybones.Cell import Cell
from drybones.FileEditingUtil import setup_file_editing_operation, finish_file_editing_operation
from drybones.Line import Line
from drybones.OptionsUtil import get_ordered_suggestions, show_ordered_suggestions
from drybones.Parse import Parse
from drybones.ParsingUtil import UNKNOWN_GLOSS, MORPHEME_DELIMITER, WORD_DELIMITER
from drybones.ProjectUtil import get_corpus_dir
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
@click.argument("drybones_fp", required=True, type=Path)
@click.argument("line_designation", required=False, type=str)
@click.option("--shuffle", "-s", type=bool, is_flag=True, help="Shuffle the lines during parsing.")
@click.option("--overwrite", "-w", type=bool, is_flag=True, help="Overwrite the input file. If false, a separate file will be created.")
@click.pass_context
def parse(ctx, drybones_fp, line_designation, shuffle, overwrite):
    """Parse text contents."""
    new_drybones_fp, lines, residues_by_location, line_designations_in_order, new_lines_by_designation, initial_hash = setup_file_editing_operation(drybones_fp, overwrite)

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
    
    orthography_case_sensitive = False  # does anyone in their right mind do this? only Klingon, I think
    # but I could see it being used for things like restricting the text to ASCII / avoiding diacritics
    #     for the purposes of typing things up easily
    
    lines_with_baselines = [line for line in lines_to_parse if line.has_baseline()]
    lines_to_parse = [line for line in lines_with_baselines if not line.is_parsed_and_glossed()]

    if len(lines_to_parse) == 0:
        if line_designation is not None:
            # user asked for a specific line, tell them what happened
            click.echo(f"Line {line_designation} is already parsed and glossed.")
        elif len(lines_with_baselines) == 0:
            click.echo(f"This file has no baselines to parse.")
        else:
            click.echo(f"This file is already completely parsed and glossed ({len(lines)} lines, {len(lines_with_baselines)} with baselines).")
    else:
        corpus_dir = get_corpus_dir(drybones_fp)
        lines_from_all_files = get_lines_from_all_drybones_files_in_dir(corpus_dir)
        known_analyses_by_word = get_known_analyses(lines_from_all_files)
        known_parses_by_word = get_known_parses(known_analyses_by_word)
        known_glosses_by_morpheme = get_known_glosses(known_analyses_by_word)
        try:
            for line in lines_to_parse:
                known_analyses_by_word, known_parses_by_word, known_glosses_by_morpheme, new_lines_by_designation = parse_single_line(line, known_analyses_by_word, known_parses_by_word, known_glosses_by_morpheme, new_lines_by_designation)
        except KeyboardInterrupt:
            click.echo("\nQuitting parsing.")
        finally:
            finish_file_editing_operation(new_drybones_fp, residues_by_location, line_designations_in_order, new_lines_by_designation, initial_hash)

    # TODO commands to implement when reading user input (no matter what input we are expecting, if we get a command then go do that instead)
    # :b = go back
    # :{designation} = go re-parse line of this designation
    # :q = quit


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

