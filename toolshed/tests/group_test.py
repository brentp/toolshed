from toolshed import groupby, groups_of
import os.path as op
import sys
from operator import itemgetter

def test_group():
    data = zip([1, 1, 1, 2, 2, 2], ['a', 'a', 'b', 'c', 'd', 'f'])


    res = list(groupby(data, (0, 1)))
    for key, grp in res:
        assert isinstance(grp, list)
        assert len(set(grp)) == 1


    res1 = list(groupby(data, 0))
    res2 = list(groupby(data, itemgetter(0)))
    assert res1 == res2

def test_groups_of():
    try:
        iterable = xrange(5)
    except:
        iterable = range(5)
    r = list(groups_of(2, iterable))
    assert r == [[0, 1], [2, 3], [4,]], r

