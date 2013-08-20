from .files import reader, tokens, nopen, header, is_newer_b
import sys
from .pool import pool, pmap

try:
    from optimize import shedskinner
except ImportError:
    pass

from itertools import groupby as igroupby
from operator import itemgetter

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

