"""
simple functions for creating nice multiprocessing pools

for example, if we have a function with signature:

    fn(a, b)

in order to use multiprocessing.Pool.imap, we'd have to write
a wrapper function:

    def wrapper(args):
        return fn(args[0], args[1]) # or fn(*args)

here, we can use pmap(fn, [(1, 1), (2, 2), (3, 3)])
and it will call: fn(1, 1), fn(2, 2), fn(3, 3)

likewise, if the only argument is a dict, then it will
expands as fn(**kwargs).

The other feature is simply to

"""
import signal
from itertools import izip

__all__ = ['pool', 'pmap']

# from aljunberg:  https://gist.github.com/aljungberg/626518 
from multiprocessing.pool import IMapIterator
def wrapper(func):
    def wrap(self, timeout=None):
        return func(self, timeout=timeout or 1e100)
    return wrap
IMapIterator.next = wrapper(IMapIterator.next)


def pool_sig():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def pool(n=None, dummy=True):
    """
    create a multiprocessing pool that responds to interrupts.
    """

    if dummy:
        from multiprocessing.dummy import Pool
    else:
        from multiprocessing import Pool

    return Pool(n, pool_sig)


class _func_star(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, args):
        f = self.f
        if isinstance(args, dict):
            return f(**args)
        elif hasattr(args, "__iter__"):
            return f(*args)
        else:
            return f(args)

def pmap(f, iterable, n=None, dummy=False, p=None):
    """
    parallel map of a function to an iterable
    if each item in iterable is itself an iterable, then
    automatically call f(*item) instead of f(item)

    Arguments:
      f: function
      iterable: any iterable where each item is sent to f
      n: number of cpus (default is number on machine)
      dummy: use dummy pool.
      p: existing pool to re-use
    """

    if p is None:
        po = pool(n, dummy)
    else:
        po = p
    assert hasattr(po, 'imap')
    f = _func_star(f)
    for r in po.imap(f, iterable):
        yield r

    # explicitly clean up created pool
    if p is None:
        po.terminate()
        po.close()
