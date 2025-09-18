import click
from typing import List


COMMAND_CHAR = ":"


class BasicREPL:
    def __init__(self, session_type_str: str):
        self.session_type_str = session_type_str

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_traceback):
        # https://docs.python.org/3/library/stdtypes.html#typecontextmanager
        # "The exception passed in should never be reraised explicitly - instead, this method should return a false value to indicate that the method completed successfully and does not want to suppress the raised exception.""

        if exc_type is KeyboardInterrupt:
            exit_str = f"\nQuitting {self.session_type_str} session."
            click.echo(exit_str)
            suppress_exceptions = True
        else:
            # if we know what to do with specific exceptions, we can echo something and then raise click.Abort(), but if we see something we haven't planned for then it should be raised
            suppress_exceptions = False

        return suppress_exceptions

    def prompt(self, prompt_str):
        inp = input(prompt_str)
        try:
            directive = get_directive_from_command(inp)
            s = None
        except NotACommandException:
            s = inp
            directive = None
        return s, directive



def get_directive_from_command(s: str) -> List[str]:
    if s.startswith(COMMAND_CHAR):
        return s[1:].split()
    else:
        raise NotACommandException


class NotACommandException(Exception):
    pass
