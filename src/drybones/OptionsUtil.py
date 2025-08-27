# helper functions about presenting lists of options to the user and getting user selections from those lists


def get_ordered_suggestions(key, known_dict, n: int=None):
    possibles = known_dict[key]
    lst = [k for k,v in sorted(possibles.items(), key=lambda kv: kv[-1], reverse=True)]
    if n is not None:
        return lst[:n]
    else:
        return lst


def show_ordered_suggestions(ordered_suggestions, n=5, display_func=None, string_if_no_options=None, string_if_options=None) -> None:
    if display_func is None:
        display_func = lambda x: x
    if string_if_no_options is None:
        string_if_no_options = "no suggestions found"
    if len(ordered_suggestions) == 0:
        click.echo(string_if_no_options)
    else:
        click.echo(string_if_options)
        n = min(n, len(ordered_suggestions))
        for i in range(n):
            s = display_func(ordered_suggestions[i])
            click.echo(f"{i+1}. {s}")