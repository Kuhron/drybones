import click
from collections import Counter, defaultdict

from drybones.Cell import Cell
from drybones.DiacriticsUtil import get_char_to_alternatives_dict, translate_diacritic_alternatives_in_string
from drybones.Parse import Parse
from drybones.ParsingUtil import UNKNOWN_GLOSS, MORPHEME_DELIMITER, WORD_DELIMITER
from drybones.Row import Row
from drybones.RowLabel import DEFAULT_BASELINE_LABEL, DEFAULT_PARSE_LABEL, DEFAULT_GLOSS_LABEL
from drybones.StringUtil import remove_punctuation
from drybones.OptionsUtil import get_ordered_suggestions, show_ordered_suggestions
from drybones.WordAnalysis import WordAnalysis


def get_known_analyses(lines, match_diacritics=False):
    d = get_char_to_alternatives_dict()
    known_analyses_by_word = defaultdict(Counter)
    baseline_label = DEFAULT_BASELINE_LABEL
    parse_label = DEFAULT_PARSE_LABEL
    gloss_label = DEFAULT_GLOSS_LABEL
    for l in lines:
        try:
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
                        bl_str = get_word_key_from_baseline_word(bl_cell.to_str(), diacritics_dict=d)
                        if match_diacritics:
                            key_str = bl_str
                        else:
                            key_str = translate_diacritic_alternatives_in_string(bl_str, d, to_base=True)
                        morpheme_strs = parse_cell.strs
                        parse = Parse(morpheme_strs)
                        glosses = gloss_cell.strs
                        analysis = WordAnalysis(bl_str, parse, glosses)
                        known_analyses_by_word[key_str][analysis] += 1
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
        except KeyboardInterrupt:
            # so it doesn't print "Error in {some random line}" if user interrupts, as this is confusing because there is not actually an error in that line, it is just what the function was in the middle of processing when it got interrupted
            raise
        except:
            print(f"\nError in line:\n{l.to_string_for_drybones_file()}")
            raise
    
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


def get_word_key_from_baseline_word(word, diacritics_dict, match_diacritics=False):
    if match_diacritics:
        key_str = word
    else:
        key_str = translate_diacritic_alternatives_in_string(word, diacritics_dict, to_base=True)
    return remove_punctuation(key_str.lower())
