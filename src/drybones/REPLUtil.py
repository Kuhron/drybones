# functions for dealing with REPLs
# especially for parsing and processing commands passed to it
# want the command sub-language to be very simple, not like click CLI
# no optional args, no kwargs, ideally a constant small number of args per command
# more complicated stuff should be done in click commands themselves, not hacked up by me via string parsing

import click
from typing import List, Tuple

from drybones.InvalidInput import InvalidInput



class REPLCommandArgs:
    def __init__(self):
        pass


def unpack_args(args_passed, arg_names) -> REPLCommandArgs | type:
    # checks for correct arg count
    if len(set(arg_names)) != len(arg_names):
        raise Exception(f"arg names should be unique: {arg_names}")

    if len(args_passed) != len(arg_names):
        click.echo(f"args should be: {arg_names}\ngot {len(args_passed)} args instead of the required {len(arg_names)}")
        return InvalidInput

    args_obj = REPLCommandArgs()
    for arg_passed, arg_name in zip(args_passed, arg_names, strict=True):
        args_obj.__setattr__(arg_name, arg_passed)
    return args_obj


def validate_int(s: str, min_value: int | None = None, max_value: int | None = None) -> int | type:
    try:
        val = int(s)
    except ValueError:
        click.echo(f"should be parseable int: {s!r}")
        return InvalidInput

    if (min_value is not None and val < min_value) or (max_value is not None and val > max_value):
        click.echo(f"int must be between {min_value} and {max_value}, inclusive, but got {val}")
        return InvalidInput
    return val
