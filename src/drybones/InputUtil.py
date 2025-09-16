# functions about getting raw input from the user

import click


def multiline_input(prompt_str: str) -> str:
    # https://stackoverflow.com/questions/30239092/how-to-get-multiline-input-from-the-user
    contents = []
    while True:
        try:
            line = input(prompt_str)
        except EOFError:
            break
        contents.append(line)
    return "\n".join(contents)
