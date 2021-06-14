def parse_args(args):
    """
    Function takes the args that is passed in through the
        --script-args from the manage.py runscript and parses
            it in the following method:
    Returns a tuple with 2 elements:
        - Element with specified args (Without a a value)
        - Dictionary with keys and values specified (Splitting with =)
    :param args:
    :return:
    """
    t = []
    key_values = {}
    for arg in args:
        if "=" in arg:
            k = arg.split("=")[0]
            v = arg.split("=")[1]
            key_values[k] = v
        else:
            t.append(arg)

    return t, key_values
