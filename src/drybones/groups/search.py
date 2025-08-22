# things relating to searching by string/regex in whichever rows
# this is NOT about searching for row labels themselves; it is about the row contents

import click
import os
import yaml
import shutil
import re
from pathlib import Path

# terminal color printing
from colorama import init as colorama_init
from colorama import Fore, Back, Style
colorama_init()

from drybones.ProjectUtil import get_corpus_dir
from drybones.ReadingUtil import get_lines_from_all_drybones_files_in_dir
from drybones.RowLabel import RowLabel, DEFAULT_LINE_DESIGNATION_LABEL


# @click.group(no_args_is_help=True)
@click.command(no_args_is_help=True)
@click.argument("row_query")
@click.argument("text_query")
def search(row_query: str, text_query: str):
    # TODO test this function on various possibilities for m/, r/, rm/, and plain substring search (no marker)
    """Search row contents using string/regex match. For `row_query` and `text_query`, begin the argument with 'm/' for simple full match, 'r/' for regex search, 'rm/' for regex full match, and nothing for simple string search (or 's/' to force simple string search in order to escape special characters). While this function is being developed and tested, you will probably get better results from just using `grep` or another well-established regex search function."""

    string_match_marker = "m/"
    regex_search_marker = "r/"
    regex_match_marker = "rm/"
    explicit_string_search_marker = "s/"

    is_regex_is_match = lambda s: (
        (s.startswith(regex_search_marker) or s.startswith(regex_match_marker)),
        (s.startswith(string_match_marker) or s.startswith(regex_match_marker)),
        strip_marker(s)
    )

    strip_single_marker = lambda s, marker: (s[len(marker):], True) if s.startswith(marker) else (s, False)

    def strip_marker(original_s, enforce_only_one_marker=False):
        s = original_s
        
        if s.startswith(explicit_string_search_marker):
            # this one behaves differently: if the string starts with it, accept the rest as a raw string and don't check for other markers; who knows, maybe user wants to search for the actual string "r/a" or something that we don't want the command to parse
            # doesn't matter if enforce_only_one_marker is true
            return s[len(explicit_string_search_marker):]
        # otherwise, check for the other special markers
        
        already_changed = False  # for enforcing only one marker on the string        
        for marker in [string_match_marker, regex_search_marker, regex_match_marker]:
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

    row_query_is_regex, row_query_is_match, row_query_stripped = is_regex_is_match(row_query)
    text_query_is_regex, text_query_is_match, text_query_stripped = is_regex_is_match(text_query)

    click.echo(f"Searching rows labeled with {'regex' if row_query_is_regex else 'string'} {row_query_stripped!r} ({'full match' if row_query_is_match else 'partial search'}) for {'regex' if text_query_is_regex else 'string'} {text_query_stripped!r} ({'full match' if text_query_is_match else 'partial search'}).\n")

    corpus_dir = get_corpus_dir(Path.cwd())
    print(f"{corpus_dir = }")
    lines_from_all_files = get_lines_from_all_drybones_files_in_dir(corpus_dir)
    # later possible optimization: only get the rows that match in the first place, don't get all rows from all files

    def regex_pattern_matches_input(pattern, test_string, full_match: bool):
        re_func = re.match if full_match else re.search
        return re_func(pattern, test_string)
    
    def string_pattern_matches_input(pattern, test_string, full_match: bool):
        s_func = (lambda patrn, test_str: patrn == test_str) if full_match else (lambda patrn, test_str: patrn in test_str)
        return s_func(pattern, test_string)

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

    # TODO print with highlighted 
    # TODO add flag for case-insensitive
    # TODO add custom pseudo-chars user can define, like [DS] to be replaced with regex "(pa|mana|ne|p[ui](n)a)"

