# things relating to timestamps, when in a recording a given line is found

import click
import pympi
from pathlib import Path
from math import floor, ceil

from drybones.DiacriticsUtil import get_char_to_alternatives_dict, translate_diacritic_alternatives_in_string
from drybones.ProjectUtil import get_corpus_dir
from drybones.TextUtil import select_lines_from_text_by_names
from drybones.RowLabel import DEFAULT_BASELINE_LABEL, DEFAULT_BASELINE_RAW_LABEL
from drybones.TextUtil import get_original_transcript_file_from_text_name, validate_text_name, get_all_texts_in_dir
from drybones.Validation import Invalidated


@click.command(no_args_is_help=True)
@click.argument("text_name", type=str)
@click.argument("line_name", required=True, type=str)
@click.pass_context
def time(ctx, text_name: str, line_name: str):
    """View timestamps of line."""
    # TODO figure out how to reduce this boilerplate that's getting repeated in various commands (opening the corpus and verifying the text)
    corpus_dir = get_corpus_dir(Path.cwd())
    text_name_validation = validate_text_name(text_name, corpus_dir, name_to_text=None)
    if text_name_validation is None or type(text_name_validation) is Invalidated:
        return
    text_name = text_name_validation.match

    lines = select_lines_from_text_by_names(text_name, [line_name], corpus_dir)
    if len(lines) == 1:
        line ,= lines
    elif len(lines) == 0:
        click.echo("lines not found", err=True)
        raise click.Abort()
    else:
        raise ValueError(f"got multiple lines from {line_name = !r}; should not be possible yet")

    baseline_raw = line.get(DEFAULT_BASELINE_RAW_LABEL)
    baseline = line.get(DEFAULT_BASELINE_LABEL)
    if baseline_raw is not None:
        baseline_raw = baseline_raw.get_contents().strip()
        print(f"{DEFAULT_BASELINE_RAW_LABEL}: {baseline_raw}")
    if baseline is not None:
        baseline = baseline.get_contents().strip()
        print(f"{DEFAULT_BASELINE_LABEL}: {baseline}")

    eaf_fp = get_original_transcript_file_from_text_name(text_name, corpus_dir, name_to_text=None)
    if not eaf_fp.exists():
        click.echo(f"Text {text_name!r} has no original .eaf file; expected to find one at:\n{eaf_fp}", err=True)
        raise click.Abort()
    
    eaf = pympi.Elan.Eaf(eaf_fp)
    tier_names = eaf.get_tier_names()
    assert list(tier_names) == ["Transcription", "Phrase Free Translation"]
    targlang_annotations = eaf.get_annotation_data_for_tier("Transcription")
    contlang_annotations = eaf.get_annotation_data_for_tier("Phrase Free Translation")

    # TODO ideally the BaselineRaw is EXACTLY what is in the eaf, so it shouldn't have been converted during accent conversion, need to figure out what to do about this, could have those lines skipped when converting any file that ends in ".dry"? could have an option to the convert-file command about this?
    diacritics_dict = get_char_to_alternatives_dict()
    baseline_raw_to_query = translate_diacritic_alternatives_in_string(baseline_raw, diacritics_dict) if baseline_raw is not None else None
    baseline_to_query = translate_diacritic_alternatives_in_string(baseline, diacritics_dict) if baseline is not None else None

    match_found = False
    for x,y in zip(targlang_annotations, contlang_annotations, strict=True):
        start_ms, end_ms, targlang_text = x
        start_ms2, end_ms2, contlang_text, targlang_text2 = y
        assert start_ms == start_ms2 and end_ms == end_ms2, "mismatched start and end times in annotation"
        assert targlang_text == targlang_text2, "mismatched transcription in annotation"
        targlang_text = translate_diacritic_alternatives_in_string(targlang_text, diacritics_dict)
        targlang_text = targlang_text.strip()

        baseline_raw_match = targlang_text == baseline_raw_to_query
        baseline_match = targlang_text == baseline_to_query
        match = baseline_raw_match or baseline_match
        if match:
            if baseline_raw_match and baseline_match:
                match_type_str = f"both {DEFAULT_BASELINE_RAW_LABEL} and {DEFAULT_BASELINE_LABEL} match"
            elif baseline_raw_match:
                match_type_str = f"{DEFAULT_BASELINE_RAW_LABEL} matches"
            elif baseline_match:
                match_type_str = f"{DEFAULT_BASELINE_LABEL} matches"
            else:
                raise Exception("impossible")
            start_mins, start_secs = ms_to_mins_and_secs(start_ms, rounding_type="floor")
            end_mins, end_secs = ms_to_mins_and_secs(end_ms, rounding_type="ceiling")
            print(f"{start_ms}-{end_ms} ms\n({text_name} {start_mins}:{start_secs:02d}-{end_mins}:{end_secs:02d})\n{match_type_str}")
            match_found = True
    if not match_found:
        click.echo(f"No lines were found that matched\n{DEFAULT_BASELINE_RAW_LABEL.with_after_label_char()} {baseline_raw_to_query}\n{DEFAULT_BASELINE_LABEL.with_after_label_char()} {baseline_to_query}")


def ms_to_mins_and_secs(ms, rounding_type="round"):
    s = ms / 1000
    if rounding_type == "round":
        s = round(s, 0)
    elif rounding_type == "floor":
        s = floor(s)
    elif rounding_type == "ceiling":
        s = ceil(s)
    else:
        raise ValueError(f"unknown rounding type: {rounding_type!r}")  # raise error for dev, not for user
    
    assert type(s) is int
    mins, secs = divmod(s, 60)
    return mins, secs
