# things related to showing what's in a text without editing anything

import click

import ReadingUtil as ru
import PrintingUtil as pu
import ProjectUtil as ju
import StringValidation as sv


@click.command
@click.argument("text_name")
@click.argument("line_number", required=False, type=int)
@click.pass_context
def read(ctx, text_name, line_number):
    """View text contents without editing."""
    text_name_validation = validate_text_name(text_name)
    if text_name_validation is None or type(text_name_validation) is sv.Invalidated:
        return
    text_name = text_name_validation.match
    click.echo(f"Reading text {text_name}", err=True)

    line_numbers_to_read = None
    if line_number is None:
        # read the whole text, leave line numbers as None
        pass
    else:
        if type(validate_line_number(line_number)) is sv.Invalidated:
            return
        line_numbers_to_read = [line_number]
    line_sets = ru.get_line_sets_from_text_name(text_name)  # should make a cache so it's not re-parsing the whole text file every time user runs a command
    if line_numbers_to_read is not None:
        line_sets = [line_sets[i-1] for i in line_numbers_to_read]
    aligned_line_labels = ctx.obj.aligned_line_labels
    pu.print_line_sets_in_pager(line_sets, aligned_line_labels)


def validate_text_name(text_name):
    text_name_options = ju.get_text_names()
    validation = sv.validate_string(text_name, text_name_options)
    if validation is None:
        return None
    elif type(validation) is sv.Invalidated:
        click.echo(f"Text name {text_name!r} not recognized. Did you mean one of these?\n  " + "\n  ".join(validation.options), err=True)
    return validation


def validate_line_number(line_number):
    try:
        int(line_number)
    except (TypeError, ValueError):
        click.echo(f"Line number should be an integer, but got {line_number!r}.", err=True)
        return False
    # check if the text has this many lines
    click.echo("validate_line_number not implemented", err=True)


