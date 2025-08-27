# helper functions for manipulating strings more generally


import click


def remove_punctuation(word_str):
    # for purposes of identifying if we have a parse of this word
    res = word_str
    try:
        while any(res.endswith(x) for x in [".", ",", "?", "!", ";", ")", "\""]):
            res = res[:-1]
        while any(res.startswith(x) for x in ["(", "\""]):
            res = res[1:]
    except IndexError:
        click.echo(f"removing punctuation from {word_str!r} resulted in blank string", err=True)
        raise click.Abort()
    return res
