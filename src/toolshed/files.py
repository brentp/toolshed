"""
    %prog [options] files
"""
import sys
import gzip
import bz2


def nopen(f, mode="rb"):
    """
    open a file that's gzipped or return stdin for '-'

    >>> nopen('-') == sys.stdin, nopen('-', 'w') == sys.stdout
    (True, True)

    >>> nopen(sys.argv[0])
    <open file '...', mode 'r...>

    # an already open file.
    >>> nopen(open(sys.argv[0]))
    <open file '...', mode 'r...>
    """
    if not isinstance(f, basestring):
        return f
    return {"r": sys.stdin, "w": sys.stdout}[mode[0]] if f == "-" \
         else gzip.open(f, mode) if f.endswith(".gz") \
         else bz2.BZ2File(f, mode) if f.endswith((".bz", ".bz2")) \
         else open(f, mode)


def tokens(line, sep="\t"):
    r"""
    >>> tokens("a\tb\tc\n")
    ['a', 'b', 'c']
    """
    return line.rstrip("\r\n").split(sep)


def reader(fname, header=True, sep="\t"):
    r"""
    for each row in the file `fname` generate dicts if `header` is True
    or lists if `header` is False. The dict keys are drawn from the first
    line. If `header` is a list of names, those will be used as the dict
    keys.

    >>> from StringIO import StringIO
    >>> get_str = lambda : StringIO("a\tb\tname\n1\t2\tfred\n11\t22\tjane")
    >>> list(reader(get_str()))
    [{'a': '1', 'b': '2', 'name': 'fred'},
     {'a': '11', 'b': '22', 'name': 'jane'}]

    >>> list(reader(get_str(), header=False))
    [['a', 'b', 'name'], ['1', '2', 'fred'], ['11', '22', 'jane']]
    """
    line_gen = (l.rstrip("\r\n").split(sep) for l in nopen(fname))
    if header == True:
        header = line_gen.next()
        header[0] = header[0].lstrip("#")

    if header:
        for toks in line_gen:
            yield dict(zip(header, toks))
    else:
        for toks in line_gen:
            yield toks

if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE).failed == 0:
        pass
