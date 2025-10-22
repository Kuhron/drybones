# things relating to searching by string/regex in whichever rows
# this is NOT about searching for row labels themselves; it is about the row contents

import click
import os
import yaml
import shutil
import re
import shlex
from pathlib import Path
from typing import List

# terminal color printing
from colorama import init as colorama_init
from colorama import Fore, Back, Style
colorama_init()

from drybones.DiacriticsUtil import get_char_to_alternatives_dict, translate_diacritic_alternatives_in_string
from drybones.InvalidInput import InvalidInput
from drybones.ProjectUtil import get_corpus_dir
from drybones.ReadingUtil import get_lines_from_all_drybones_files_in_dir
from drybones.RowLabel import RowLabel, DEFAULT_LINE_DESIGNATION_LABEL
from drybones.SearchResult import SearchResult
from drybones.StringMatch import StringMatch


STRING_MATCH_MARKER = "m/"
REGEX_SEARCH_MARKER = "r/"
REGEX_MATCH_MARKER = "rm/"
EXPLICIT_STRING_SEARCH_MARKER = "s/"

REPEAT_CHAR, REPEAT_CHAR_INDEF, REPEAT_CHAR_PLURAL = ";", "a semicolon", "semicolons"
# REPEAT_CHAR, REPEAT_CHAR_INDEF, REPEAT_CHAR_PLURAL = ":", "a colon", "colons"

PROMPT_STR = "> "


# @click.group(no_args_is_help=True)
@click.command(no_args_is_help=False)
@click.argument("row_query", required=False)
@click.argument("text_query", required=False)
@click.option("--interactive", "-i", type=bool, is_flag=True, help="Open an interactive session to run multiple search queries (one at a time) while keeping the corpus loaded into RAM.")
def search(row_query: str, text_query: str, interactive: bool):
    # TODO test this function on various possibilities for m/, r/, rm/, and plain substring search (no marker)
    """Search row contents using string/regex match. For `row_query` and `text_query`, begin the argument with 'm/' for simple full match, 'r/' for regex search, 'rm/' for regex full match, and nothing for simple string search (or 's/' to force simple string search in order to escape special characters). While this function is being developed and tested, you will probably get better results from just using `grep` or another well-established regex search function."""

    corpus_dir = get_corpus_dir(Path.cwd())
    print(f"{corpus_dir = }")
    lines_from_all_files = get_lines_from_all_drybones_files_in_dir(corpus_dir)
    diacritic_dict = get_char_to_alternatives_dict()
    click.echo()  # to add space between the "loaded lines from ..." and the input prompt

    qsum = (row_query is not None) + (text_query is not None)
    if qsum == 0:
        # open an interactive session, whether the user specified -i or not
        run_interactive_search_session(lines_from_all_files, diacritic_dict)
    elif qsum == 2:
        # do a search query immediately based on the args passed
        if interactive:
            # do the initial query and then continue as an interactive session
            run_interactive_search_session(lines_from_all_files, diacritic_dict, initial_row_query=row_query, initial_text_query=text_query)
        else:
            # do this query only, do not continue into interactive session
            search_results = run_search_query(row_query, text_query, lines_from_all_files, diacritic_dict)
            process_search_results(search_results)
    else:
        click.echo("`row_query` and `text_query` should either both be passed or both be omitted", err=True)
        raise click.Abort()

    # TODO print with highlighted 
    # TODO add flag for case-insensitive
    # TODO add custom pseudo-chars user can define, like [DS] to be replaced with regex "(pa|mana|ne|p[ui](n)a)"


def run_interactive_search_session(lines_from_all_files, diacritic_dict, initial_row_query=None, initial_text_query=None):
    last_row_query = None
    last_text_query = None

    if (initial_row_query is not None) or (initial_text_query is not None):
        if not ((initial_row_query is not None) and (initial_text_query is not None)):
            click.echo("`row_query` and `text_query` should either both be passed or both be omitted", err=True)
            raise click.Abort()
        run_initial = True
    else:
        run_initial = False

    while True:
        if run_initial:
            row_query = initial_row_query
            text_query = initial_text_query
            run_initial = False
        else:
            try:
                query_from_user = get_query_from_user(last_row_query, last_text_query)
                if query_from_user is InvalidInput:
                    continue
                else:
                    row_query, text_query = query_from_user
            except KeyboardInterrupt:
                click.echo("\n")
                continue
            except EOFError:
                click.echo("\nQuitting search session.")
                return
        
        search_results = run_search_query(row_query, text_query, lines_from_all_files, diacritic_dict)
        last_row_query = row_query
        last_text_query = text_query
        process_search_results(search_results)
        click.echo()


def run_search_query(row_query, text_query, lines_from_all_files, diacritic_dict):
    row_query_is_regex, row_query_is_match, row_query_stripped = is_regex_is_match(row_query)
    text_query_is_regex, text_query_is_match, text_query_stripped = is_regex_is_match(text_query)

    click.echo(f"Searching rows labeled with {'regex' if row_query_is_regex else 'string'} {row_query_stripped!r} ({'full match' if row_query_is_match else 'partial search'}) for {'regex' if text_query_is_regex else 'string'} {text_query_stripped!r} ({'full match' if text_query_is_match else 'partial search'}).\n")

    # later possible optimization: only get the rows that match in the first place, don't get all rows from all files

    # TODO add option for user to require matching diacritics (e.g. imagine searching a corpus of Vietnamese and you don't want all the words that differ only in diacritics from your query)
    convert = lambda s: translate_diacritic_alternatives_in_string(s, diacritic_dict, to_base=True)

    row_match_func = lambda test_str: get_regex_matches(row_query_stripped, convert(test_str), full_match=row_query_is_match) if row_query_is_regex else get_string_matches(row_query_stripped, convert(test_str), full_match=row_query_is_match)
    text_match_func = lambda test_str: get_regex_matches(text_query_stripped, convert(test_str), full_match=text_query_is_match) if text_query_is_regex else get_string_matches(text_query_stripped, convert(test_str), full_match=text_query_is_match)

    rows_to_search = []
    for line in lines_from_all_files:
        for row in line.rows:
            matches = row_match_func(row.label.string)
            if len(matches) > 0:
                tup = (row, line)  # want reference back to the parent line so user can see where it is
                rows_to_search.append(tup)

    search_results = []
    for row, line in rows_to_search:
        contents = row.get_contents()
        matches = text_match_func(contents)
        if len(matches) > 0:
            sr = SearchResult(string=contents, spans=[m.span() for m in matches], row=row, line=line)
            search_results.append(sr)

    return search_results


def print_search_results(search_results):
    if len(search_results) > 0:
        click.echo("\nSearch results:\n")
        for i, sr in enumerate(search_results):
            click.echo(f"{i+1}) {Fore.YELLOW}{DEFAULT_LINE_DESIGNATION_LABEL}: {sr.line.designation} / {sr.row.label.string}:{Style.RESET_ALL} {sr.get_highlighted_string()}")
        click.echo()
    else:
        click.echo("\nNo results found.")


def get_query_from_user(last_row_query, last_text_query):
    click.echo(f"Type your row and text queries, separated by space. Use quotation marks around either of these if it contains spaces. To repeat the last row or text query, type {REPEAT_CHAR_INDEF} ({REPEAT_CHAR}) as the query. To repeat the last search, type {REPEAT_CHAR_PLURAL} ({REPEAT_CHAR*2}).")
    raw = prompt("query")
    if raw.replace(" ", "") == REPEAT_CHAR*2:  # because shlex will split on arbitrary number of spaces, and we want "; ;" to behave the same as ";;" (where ';' is the REPEAT_CHAR)
        if last_row_query is None and last_text_query is None:
            click.echo("Last row and text query must both be defined, but neither is.\n")
            return InvalidInput
        elif last_row_query is None:
            click.echo("Last row and text query must both be defined, but the row query is not.\n")
            return InvalidInput
        elif last_text_query is None:
            click.echo("Last row and text query must both be defined, but the text query is not.\n")
            return InvalidInput
        else:
            return last_row_query, last_text_query
    else:
        try:
            row_query, text_query = shlex.split(raw)  # preserve quoted substrings that have space in them
        except ValueError:
            click.echo("invalid input\n")
            return InvalidInput
        
        if row_query == REPEAT_CHAR:
            if last_row_query is None:
                click.echo("Last row and text query must both be defined, but the row query is not.\n")
                return InvalidInput
            else:
                row_query = last_row_query
        if text_query == REPEAT_CHAR:
            if last_text_query is None:
                click.echo("Last row and text query must both be defined, but the text query is not.\n")
                return InvalidInput
            else:
                text_query = last_text_query
    
    return row_query, text_query


def strip_marker(original_s, enforce_only_one_marker=False):
    s = original_s
    
    if s.startswith(EXPLICIT_STRING_SEARCH_MARKER):
        # this one behaves differently: if the string starts with it, accept the rest as a raw string and don't check for other markers; who knows, maybe user wants to search for the actual string "r/a" or something that we don't want the command to parse
        # doesn't matter if enforce_only_one_marker is true
        return s[len(EXPLICIT_STRING_SEARCH_MARKER):]
    # otherwise, check for the other special markers
    
    already_changed = False  # for enforcing only one marker on the string        
    for marker in [STRING_MATCH_MARKER, REGEX_SEARCH_MARKER, REGEX_MATCH_MARKER]:
        if enforce_only_one_marker:
            s, changed = strip_single_marker(s, marker)
            if already_changed and changed:
                raise ValueError(f"string {original_s!r} starts with more than one special marker for regex/match functionality")
            elif changed:
                already_changed = True
        else:
            # just take the first one
            s, changed = strip_single_marker(s, marker)
            if changed:
                break
    return s


def is_regex_is_match(s):
    is_regex = s.startswith(REGEX_SEARCH_MARKER) or s.startswith(REGEX_MATCH_MARKER)
    is_match = s.startswith(STRING_MATCH_MARKER) or s.startswith(REGEX_MATCH_MARKER)
    s_stripped = strip_marker(s)
    return is_regex, is_match, s_stripped


def strip_single_marker(s, marker):
    return (s[len(marker):], True) if s.startswith(marker) else (s, False)


def get_regex_matches(pattern, test_string, full_match: bool) -> List[re.Match]:
    if full_match:
        m = re.fullmatch(pattern, test_string)
        return [m] if m is not None else []
    else:
        # list of re.Match objects
        return list(re.finditer(pattern, test_string))


def get_string_matches(pattern, test_string, full_match: bool) -> List[StringMatch]:
    if full_match:
        return [StringMatch(test_string, 0, len(test_string))] if pattern == test_string else []
    else:
        matches = []
        for i in range(len(test_string) - len(pattern) + 1):
            substring = test_string[i : i+len(pattern)]
            if substring == pattern:
                matches.append(StringMatch(test_string, i, i+len(pattern)))
        return matches


def process_search_results(search_results):
    print_search_results(search_results)
    while True:
        click.echo("Select the number of the result you want to investigate, or to exit the current search you can enter nothing, 'q', or 'quit'.")
        raw = prompt("choice")
        if raw in ["", "q", "quit"]:
            return
        else:
            try:
                n = int(raw)
            except ValueError:
                click.echo("invalid number\n")
                continue
        
        if 0 <= n-1 < len(search_results):
            chosen_search_result = search_results[n-1]
            process_single_search_result(chosen_search_result)
        else:
            click.echo(f"Number must be between 1 and the number of search results ({len(search_results)}), inclusive.\n")


def process_single_search_result(sr):
    # later can do some stuff here beyond just printing the search result
    # like allowing user to input commands to redo a word analysis, reparse the line, search for some other item found in this line, etc.

    click.echo(sr.to_detailed_display_str())
    click.echo()


def prompt(s):
    return input(f"{s} {PROMPT_STR}")

