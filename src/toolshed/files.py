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

dialect = csv.excel

class ProcessException(Exception): pass

def process_iter(proc, cmd):
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
                print >>sys.stderr, "cmd was:", cmd
                raise ProcessException(proc.stderr.read())
            s = proc.stderr.read().strip()
            if len(s) != 0:
                print >>sys.stderr, s

def nopen(f, mode="rb"):
    r"""
    open a file that's gzipped or return stdin for '-'
    if f is a number, the result of nopen(sys.argv[f]) is returned.

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

    >>> nopen(0)
    <open file '...', mode 'r...>

    Or provide nicer access to Popen.stdout
    >>> files = list(nopen("|ls"))
    >>> assert 'setup.py\n' in files, files
    """
    if isinstance(f, (int, long)):
        return nopen(sys.argv[f], mode)

    if not isinstance(f, basestring):
        return f
    if f.startswith("|"):
        p = Popen(f[1:], stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
        if mode and mode[0] == "r":
            return process_iter(p, f[1:])
        return p

    if f.startswith(("http://", "https://", "ftp://")):
        fh = urllib.urlopen(f)
        if f.endswith(".gz"):
            return ungzipper(fh)
        return fh
    return {"r": sys.stdin, "w": sys.stdout}[mode[0]] if f == "-" \
         else gzip.open(f, mode) if f.endswith((".gz", ".Z", ".z")) \
         else bz2.BZ2File(f, mode) if f.endswith((".bz", ".bz2", ".bzip2")) \
         else open(op.expanduser(op.expandvars(f)), mode)

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
    h = tokens(fh.next(), sep)
    h[0] = h[0].lstrip("#")
    return h

def xls_reader(f, sheet=0):
    import xlrd
    wb = xlrd.open_workbook(f, on_demand=True)
    ws = wb.sheets()[sheet]
    for irow in range(ws.nrows):
        yield map(str, ws.row_values(irow))

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
    if isinstance(fname, (int, long)):
        fname = sys.argv[fname]
    if not isinstance(fname, basestring) and \
        isinstance(fname, types.GeneratorType):
            line_gen = fname
    elif sep is None:
        import re
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
