"""
    %prog [options] files
"""
import sys
import os
import os.path as op
from itertools import izip
import urllib
from collections import OrderedDict

import gzip
import bz2
from subprocess import Popen, PIPE
import csv

dialect = csv.excel

def nopen(f, mode="rb"):
    """
    open a file that's gzipped or return stdin for '-'

    >>> nopen('-') == sys.stdin, nopen('-', 'w') == sys.stdout
    (True, True)

    >>> nopen(sys.argv[0])
    <open file '...', mode 'r...>

    # expands user and vars ($HOME)
    >>> nopen("~/.bashrc"), nopen("$HOME/.bashrc")
    (<open file '...', mode 'r...>, <open file '...', mode 'r...>)

    # an already open file.
    >>> nopen(open(sys.argv[0]))
    <open file '...', mode 'r...>

    Or provide nicer access to Popen.stdout
    >>> files = nopen("|ls").read()
    >>> assert 'setup.py' in files
    """
    if not isinstance(f, basestring):
        return f
    if f.startswith("|"):
        p = Popen(f[1:], stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
        if mode and mode[0] == "r": return p.stdout
        # if it is writable, just return the object.
        return p
    return {"r": sys.stdin, "w": sys.stdout}[mode[0]] if f == "-" \
         else gzip.open(f, mode) if f.endswith((".gz", ".Z", ".z")) \
         else bz2.BZ2File(f, mode) if f.endswith((".bz", ".bz2", ".bzip2")) \
         else urllib.urlopen(f) if f.startswith(("http://", "https://",
             "ftp://")) \
         else open(op.expanduser(op.expandvars(f)), mode)

def tokens(line, sep="\t"):
    r"""
    >>> tokens("a\tb\tc\n")
    ['a', 'b', 'c']
    """
    return line.rstrip("\r\n").split(sep)


def header(fname, sep="\t"):
    """
    just grab the header from a given file
    """
    fh = iter(nopen(fname))
    h = tokens(fh.next(), sep)
    h[0] = h[0].lstrip("#")
    return h

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
    if not isinstance(fname, basestring):
        line_gen = (l.rstrip("\r\n").split(sep) for l in nopen(fname))
    else:
        dialect = csv.excel
        dialect.delimiter = sep
        line_gen = csv.reader(nopen(fname), dialect=dialect)

    a_dict = dict
    # if header is 'ordered', then use an ordered dictionary.
    if header == "ordered":
        a_dict = OrderedDict
        header = True

    if header == True:
        header = line_gen.next()
        header[0] = header[0].lstrip("#")


    if header:
        for toks in line_gen:
            yield a_dict(izip(header, toks))
    else:
        for toks in line_gen:
            yield toks

def is_newer_b(a, bfiles):
    """
    check that all b files have been modified more recently than a
    """
    if isinstance(bfiles, basestring):
        bfiles = [bfiles]

    if not op.exists(a): return False
    if not all(op.exists(b) for b in bfiles): return False

    atime = os.stat(a).st_mtime # modification time
    for b in bfiles:
        # a has been modified since
        if atime > os.stat(b).st_mtime: 
            return False
    return True



if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE)
