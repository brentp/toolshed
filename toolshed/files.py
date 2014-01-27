"""
    %prog [options] files
"""
import sys
import os
import os.path as op
try:
    from itertools import izip
except ImportError:
    izip = zip
try:
    callable
except NameError:
    callable = lambda a: hasattr(a, "__call__")

import types
import urllib

import gzip
import bz2
from subprocess import Popen, PIPE
import csv

if sys.version_info.major < 3:
    int_types = (int, long)
    urlopen = urllib.urlopen
    basestring = basestring
else:
    int_types = (int,)
    basestring = str
    urlopen = urllib.request.urlopen

dialect = csv.excel

class ProcessException(Exception): pass

def process_iter(proc, cmd=""):
    """
    helper function to iterate over a process stdout
    and report error messages when done
    """
    try:
        for l in proc.stdout:
            yield l
    finally:
        if proc.poll() is None:
            # there was an exception
            return
        else:
            proc.wait()
            if proc.returncode not in (0, None):
                sys.stderr.write("cmd was:%s\n" % cmd)
                raise ProcessException(proc.stderr.read())
            s = proc.stderr.read().strip()
            if len(s) != 0:
                sys.stderr.write(str(s))
                sys.stderr.write('\n')

def nopen(f, mode="r"):
    r"""
    open a file that's gzipped or return stdin for '-'
    if f is a number, the result of nopen(sys.argv[f]) is returned.

    >>> nopen('-') == sys.stdin, nopen('-', 'w') == sys.stdout
    (True, True)

    >>> nopen(sys.argv[0])
    <...file...>

    # expands user and vars ($HOME)
    >>> nopen("~/.bashrc").name == nopen("$HOME/.bashrc").name
    True

    # an already open file.
    >>> nopen(open(sys.argv[0]))
    <...file...>

    >>> nopen(0)
    <...file...>

    Or provide nicer access to Popen.stdout
    >>> files = list(nopen("|ls"))
    >>> assert 'setup.py\n' in files or b'setup.py\n' in files, files
    """
    if isinstance(f, int_types):
        return nopen(sys.argv[f], mode)

    if not isinstance(f, basestring):
        return f
    if f.startswith("|"):
        # using shell explicitly makes things like process substitution work:
        # http://stackoverflow.com/questions/7407667/python-subprocess-subshells-and-redirection
        p = Popen(f[1:], stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True,
                close_fds=False, executable=os.environ.get('SHELL'))
        if mode and mode[0] == "r":
            return process_iter(p, f[1:])
        return p

    if f.startswith(("http://", "https://", "ftp://")):
        fh = urlopen(f)
        if f.endswith(".gz"):
            return ungzipper(fh)
        if sys.version_info.major < 3:
            return fh
        import io
        return io.TextIOWrapper(fh)
    f = op.expanduser(op.expandvars(f))
    if f.endswith((".gz", ".Z", ".z")):
        fh = gzip.open(f, mode)
        if sys.version_info.major < 3:
            return fh
        import io
        return io.TextIOWrapper(fh)
    elif f.endswith((".bz", ".bz2", ".bzip2")):
        fh = bz2.BZ2File(f, mode)
        if sys.version_info.major < 3:
            return fh
        import io
        return io.TextIOWrapper(fh)

    return {"r": sys.stdin, "w": sys.stdout}[mode[0]] if f == "-" \
         else open(f, mode)

def ungzipper(fh, blocksize=16384):
    """
    work-around to get streaming download of http://.../some.gz
    """
    import zlib
    uzip = zlib.decompressobj(16 + zlib.MAX_WBITS)
    data = uzip.decompress(fh.read(blocksize)).split("\n")

    while len(data[0]):
        # last chunk might not be a full line.
        save = data.pop()
        for line in data:
            yield line
        data = uzip.decompress(fh.read(blocksize)).split("\n")
        # first line is prepended with saved chunk from end of last set.
        data[0] = save + data[0]

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
    h = tokens(next(fh), sep)
    h[0] = h[0].lstrip("#")
    return h

def xls_reader(f, sheet=0):
    import xlrd
    wb = xlrd.open_workbook(f, on_demand=True)
    ws = wb.sheets()[sheet]
    for irow in range(ws.nrows):
        yield map(str, ws.row_values(irow))

def reader(fname, header=True, sep="\t", skip_while=None):
    r"""
    for each row in the file `fname` generate dicts if `header` is True
    or lists if `header` is False. The dict keys are drawn from the first
    line. If `header` is a list of names, those will be used as the dict
    keys.
    skip_while is a function that returns False when it is ready to start
    consuming. this could be something like:

    skip_while = lambda toks: toks[0].startswith('#')

    >>> import sys
    >>> if sys.version_info.major < 3:
    ...     from StringIO import StringIO
    ... else:
    ...     from io import StringIO
    >>> get_str = lambda : StringIO("a\tb\tname\n1\t2\tfred\n11\t22\tjane")
    >>> expected = [{'a': '1', 'b': '2', 'name': 'fred'},
    ... {'a': '11', 'b': '22', 'name': 'jane'}]
    >>> list(reader(get_str())) == expected
    True

    >>> expected = [['a', 'b', 'name'], 
    ...             ['1', '2', 'fred'], ['11', '22', 'jane']]
    >>> list(reader(get_str(), header=False)) == expected
    True
    """
    if isinstance(fname, int_types):
        fname = sys.argv[fname]
    if not isinstance(fname, basestring) and \
        isinstance(fname, types.GeneratorType):
            line_gen = fname
    elif sep is None:
        def _line_gen(f, sep):
            if sep is None:
                for line in nopen(f):
                    yield line.rstrip("\r\n").split()
        line_gen = _line_gen(fname, sep)
    elif isinstance(fname, basestring) and fname.endswith((".xls")):
        line_gen = xls_reader(fname)
    else:
        try:
            dialect = csv.excel
            dialect.delimiter = sep
            line_gen = csv.reader(nopen(fname), dialect=dialect)
        except TypeError: # sep is None or a regex.
            import re
            sep = re.compile(sep)
            def _re_line_gen(f, sep):
                for line in nopen(f):
                    yield sep.split(line.rstrip("\r\n"))
            line_gen = _re_line_gen(fname, sep)

    if skip_while:
        from itertools import chain
        l = next(line_gen)
        while skip_while(l):
            l = next(line_gen)
        line_gen = chain.from_iterable(([l], line_gen))

    # they sent in a class or function that accepts the toks.
    if callable(header):
        for toks in line_gen:
            yield header(toks)

        raise StopIteration

    a_dict = dict
    # if header is 'ordered', then use an ordered dictionary.
    if header == "ordered":
        from collections import OrderedDict as a_dict
        header = True

    if header == True:
        header = next(line_gen)
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
