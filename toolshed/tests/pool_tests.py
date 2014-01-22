from toolshed.pool import pool, pmap
import os.path as op

DATA = op.join(op.dirname(__file__), "data")

def test_pool():
    p1 = pool(None, dummy=False)
    assert hasattr(p1, 'imap')

    p2 = pool(None, dummy=True)
    assert hasattr(p2, 'imap')

def fn(number):
    return number * 2

def test_pmap():

    r1 = list(pmap(fn, [1, 2, 3, 4]))

    r2 = list(map(fn, [1, 2, 3, 4]))
    assert r1 == r2, (r1, r2)

def fnargs(a, b):
    return a + b

def test_pmap_args():

    args = [(1, 1), (2, 2), (3, 3), (4, 4)]

    r1 = pmap(fnargs, args)

    for res, args in zip(r1, args):
        assert res == args[0] + args[1], (res, args)

def fndict(a=3, b=None):
    return a - b

def test_pmap_kwargs():

    args = [dict(a=1, b=1), dict(a=2, b=1), dict(a=3, b=1)]
    r1 = pmap(fndict, args)
    for res, args in zip(r1, args):
        assert res == args['a'] - args['b'], (res, args)
