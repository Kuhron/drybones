# things relating to searching by string/regex in whichever rows
# this is NOT about searching for row labels themselves; it is about the row contents

import click
import os
import yaml
import shutil
import re
import shlex
from pathlib import Path

# terminal color printing
from colorama import init as colorama_init
from colorama import Fore, Back, Style
colorama_init()

from drybones.ProjectUtil import get_corpus_dir
from drybones.ReadingUtil import get_lines_from_all_drybones_files_in_dir
from drybones.RowLabel import RowLabel, DEFAULT_LINE_DESIGNATION_LABEL


STRING_MATCH_MARKER = "m/"
REGEX_SEARCH_MARKER = "r/"
REGEX_MATCH_MARKER = "rm/"
EXPLICIT_STRING_SEARCH_MARKER = "s/"


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

    qsum = (row_query is not None) + (text_query is not None)
    if qsum == 0:
        # open an interactive session, whether the user specified -i or not
        run_interactive_search_session(lines_from_all_files)
    elif qsum == 2:
        run_search_query(row_query, text_query, lines_from_all_files)
    else:
        raise Exception("`row_query` and `text_query` should either both be passed or both be omitted")

    # TODO print with highlighted 
    # TODO add flag for case-insensitive
    # TODO add custom pseudo-chars user can define, like [DS] to be replaced with regex "(pa|mana|ne|p[ui](n)a)"


def run_interactive_search_session(lines_from_all_files):
    repeat_char, repeat_char_indef, repeat_char_plural = ";", "a semicolon", "semicolons"
    # repeat_char, repeat_char_indef, repeat_char_plural = ":", "a colon", "colons"

    last_row_query = None
    last_text_query = None

    while True:
        try:
            click.echo(f"Type your row and text queries, separated by space. Use quotation marks around either of these if it contains spaces. To repeat the last row or text query, type {repeat_char_indef} ({repeat_char}) as the query. To repeat the last search, type {repeat_char_plural} ({repeat_char*2}).")
            raw = input("> ")
            if raw == repeat_char*2:
                if last_row_query is None and last_text_query is None:
                    click.echo("Last row and text query must both be defined, but neither is.")
                    continue
                elif last_row_query is None:
                    click.echo("Last row and text query must both be defined, but the row query is not.")
                    continue
                elif last_text_query is None:
                    click.echo("Last row and text query must both be defined, but the text query is not.")
                    continue
            else:
                try:
                    row_query, text_query = shlex.split(raw)  # preserve quoted substrings that have space in them
                except ValueError:
                    click.echo("invalid input\n")
                    continue
                if row_query == repeat_char:
                    row_query = last_row_query
                else:
                    last_row_query = row_query
                if text_query == repeat_char:
                    text_query = last_text_query
                else:
                    last_text_query = text_query
            run_search_query(row_query, text_query, lines_from_all_files)
            click.echo()
        except KeyboardInterrupt:
            click.echo("\nQuitting search session.")
            return


def run_search_query(row_query, text_query, lines_from_all_files):
    row_query_is_regex, row_query_is_match, row_query_stripped = is_regex_is_match(row_query)
    text_query_is_regex, text_query_is_match, text_query_stripped = is_regex_is_match(text_query)

    click.echo(f"Searching rows labeled with {'regex' if row_query_is_regex else 'string'} {row_query_stripped!r} ({'full match' if row_query_is_match else 'partial search'}) for {'regex' if text_query_is_regex else 'string'} {text_query_stripped!r} ({'full match' if text_query_is_match else 'partial search'}).\n")

    # later possible optimization: only get the rows that match in the first place, don't get all rows from all files

    row_match_func = lambda test_str: regex_pattern_matches_input(row_query_stripped, test_str, full_match=row_query_is_match) if row_query_is_regex else string_pattern_matches_input(row_query_stripped, test_str, full_match=row_query_is_match)
    text_match_func = lambda test_str: regex_pattern_matches_input(text_query_stripped, test_str, full_match=text_query_is_match) if text_query_is_regex else string_pattern_matches_input(text_query_stripped, test_str, full_match=text_query_is_match)

    rows_to_search = []
    for line in lines_from_all_files:
        for row in line.rows:
            if row_match_func(row.label.string):
                tup = (row, line.designation)  # want reference back to the parent line so user can see where it is
                rows_to_search.append(tup)

    contents_matched = []
    for row, line_designation in rows_to_search:
        contents = row.get_contents()
        if text_match_func(contents):
            tup = (contents, row.label.string, line_designation)
            contents_matched.append(tup)

    if len(contents_matched) > 0:
        click.echo("\nSearch results:\n")
        for s, row_label_str, line_designation in contents_matched:
            click.echo(f"{Fore.YELLOW}{DEFAULT_LINE_DESIGNATION_LABEL}: {line_designation} / {row_label_str}:{Style.RESET_ALL} {s}")
    else:
        click.echo("\nNo results found.")


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


def regex_pattern_matches_input(pattern, test_string, full_match: bool):
    re_func = re.match if full_match else re.search
    return re_func(pattern, test_string)


def string_pattern_matches_input(pattern, test_string, full_match: bool):
    s_func = (lambda patrn, test_str: patrn == test_str) if full_match else (lambda patrn, test_str: patrn in test_str)
    return s_func(pattern, test_string)

