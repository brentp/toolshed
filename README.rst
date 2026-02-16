Toolshed: Less Boiler-Plate |build|_
====================================

.. |build| image:: https://travis-ci.org/brentp/toolshed.svg
.. _build: https://travis-ci.org/brentp/toolshed

This is a collection of well-tested, simple modules and functions
that I use frequently.

Files
-----

If you have a "proper" CSV file with quoting and such, use python's `csv`_
module.

If all you have is a file with a header and you want to get a dictionary
for each row::

    >>> from toolshed import reader, header, nopen
    >>> for d in reader('toolshed/tests/data/file_data.txt'):
    ...    print d['a'], d['b'], d['c']
    1 2 3
    11 12 13
    21 22 23

Or as a namedtuple::

    >>> from collections import namedtuple
    >>> for d in reader('toolshed/tests/data/file_data.txt', header=namedtuple):
    ...    print d.a, d.b, d.c
    1 2 3
    11 12 13
    21 22 23

works the same for gzipped, bzipped, and .xls files and for stdin (via "-")
and for files over http/ftp::

    >>> for drow in (d for d in reader('toolshed/tests/data/file_data.txt.gz') if int(d['a']) > 10):
    ...    print drow['a'], drow['b'], drow['c']
    11 12 13
    21 22 23

if one can specify the header to a file without one using the `header=` kwarg.
If `header` is "ordered" then an OrderedDictionary will be used so that
drow.keys() and d.values() will return the values in the order they appeared in the file.

If `header` is a callable (a function or class) then, for each row, that
callable will be called for each row with a single argument which is the
list of columns in the future, it may be called as:  callable(\*row) instead
of callable(row). **comments welcome**.

the `toolshed.nopen` can open a file over http, https, ftp, a gzipped file, a
bzip file, or a subprocess with the same syntax::

    >>> nopen('toolshed/tests/data/file_data.txt.gz') # doctest: +ELLIPSIS
    <gzip open file ...>
    >>> nopen('|ls') # doctest: +ELLIPSIS
    <generator object process_iter at ...>

    #you may need to send stdin to a proc:

    # NOTE mode is None
    >>> proc = nopen("|awk '(NR % 2 == 1)'", mode=None)

    # write some stuff to STDIN
    >>> proc.stdin.write("number\n")
    >>> for i in range(5):
    ...    proc.stdin.write("%i\n" % i)

    # IMPORTANT! close stdin
    >>> proc.stdin.close()

    # the read stdout
    >>> for d in reader(proc.stdout, header=True):
    ...    print d
    {'number': '1'}
    {'number': '3'}

    #In addition, you can skip the first lines of a file with a function like::

    skipper = lambda toks: toks[0].startswith('#')
    for d in reader('file-with-extra-header.txt', skip_while=skipper):
        do_stuff(d)

Pools
-----

ctrl+c on a long-running multi-processing pool is often non-responsive.
if we use toolshed.pool(), that is fixed (using signal).

this module also provides pmap, which wraps multiprocessing.Pool.map()
to expand args, so we can do::


    >>> def fn(a, b):  return a + b

    >>> from toolshed import pmap
    >>> list(pmap(fn, [(1, 1), (2, 3)]))
    [2, 5]



and the fn will be mapped in parallel and we didn't need a wrapper function
for fn like::

    def wrapper(args):
        return fn(*args)

as we would normally.

Note that this is like::

    >>> from itertools import starmap
    >>> list(starmap(fn, [(1, 1), (2, 3)]))
    [2, 5]

But Pool.starmap is not available until python 3.3

This can cause problems in cases where your 'fn' expects
args, instead of the exploded arguments. In the future, it may introspect fn,
but that is not implemented for now.

Links
-----

.. _`csv`: http://docs.python.org/library/csv.html
