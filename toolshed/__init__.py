from .files import (reader, tokens, nopen, header, is_newer_b, int_types)
import sys
from .pool import pool, pmap
from .fmt import fmt2header

if sys.version_info[0] == 3:
    basestring = str

from itertools import groupby as igroupby
from operator import itemgetter

__version__ = "0.4.7"

def groupby(iterable, key=0, filter=None):
    """
    wrapper to itertools.groupby that returns a list of each group, rather
    than a generator and accepts integers or strings as the key and
    automatically converts them to callables with itemgetter(key)

    Arguments:
        iterable: iterable
        key: string, int or callable that tells how to group

    Returns:
        an iterable where each item is the key and a *list* of that
        group. (itertools.groupby returns a generator of that group).

    e.g. groupby(iterable, 0)
    """
    if isinstance(key, (basestring, int)):
        key = itemgetter(key)
    elif isinstance(key, (tuple, list)):
        key = itemgetter(*key)
    for label, grp in igroupby(iterable, key):
        yield label, list(grp)

try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest as izip_longest

def groups_of(n, iterable):
    """
    >>> groups_of(2, range(5))
    """
    args = [iter(iterable)] * n
    for x in izip_longest(*args):
        yield [v for v in x if v is not None]

def main():
    #import argparse
    #p = argparse.ArgumentParser(__doc__)
    print("main")
    pass


if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE).failed == 0:
        main()

