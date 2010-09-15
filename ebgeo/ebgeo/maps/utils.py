PAIR_SEP = "|"
KEY_VALUE_SEP = ":"

def encode_theme_data(data):
    """
    Encodes a dictionary suitable for passing theme data in a URI to the
    map server.

    Assumes URI encoding will be handled upstream.

    >>> d = {"logan-square": 54, "edgewater": 31, "the-loop": 44}
    >>> s = encode_theme_data(d)
    >>> s == 'the-loop:44|logan-square:54|edgewater:31'
    True
    """
    return PAIR_SEP.join(["%s%s%s" % (k, KEY_VALUE_SEP, v) for k, v in data.items()])

def decode_theme_data(s):
    """
    Decodes a string that's been encoding by encode_theme_data() and
    returns a dictionary.

    Assumes already URI-decoded.

    >>> d = decode_theme_data("the-loop:44|logan-square:54|edgewater:31")
    >>> d == {"logan-square": 54, "edgewater": 31, "the-loop": 44}
    True
    """
    pairs = [s.split(KEY_VALUE_SEP) for s in s.split(PAIR_SEP)]
    return dict([(k, float(v)) for k, v in pairs])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
