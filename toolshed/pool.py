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
from itertools import izip, repeat
SIGNAL = signal.signal(signal.SIGINT, signal.SIG_IGN)

__all__ = ['pool', 'pmap']

def pool_sig():
    return SIGNAL

def pool(n=None, dummy=True):
    """
    create a multiprocessing pool that responds to interrupts.
    """
    if dummy:
        from multiprocessing.dummy import Pool
    else:
        from multiprocessing import Pool
    return Pool(n, pool_sig)

def _func_star(args):
    if isinstance(args[1], dict):
        return args[0](**args[1])
    elif hasattr(args[1], "__iter__"):
        return args[0](*args[1])
    else:
        return args[0](args[1])

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

    # just create repeated func, so we can /apply/ it across the
    # iterable via the func_star function above
    iterable = izip(repeat(f), iterable)

    if p is None:
        p = pool(n, dummy)
    else:
        assert hasattr(p, 'imap')

    return p.imap(_func_star, iterable)
