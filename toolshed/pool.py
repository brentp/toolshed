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

__all__ = ['pool', 'pmap']

import itertools as it
# from aljunberg:  https://gist.github.com/aljungberg/626518
from multiprocessing.pool import IMapIterator
def wrapper(func):
    def wrap(self, timeout=None):
        return func(self, timeout=timeout or 1e10)
    return wrap
import sys
if sys.version_info[0] < 3:
    IMapIterator.next = wrapper(IMapIterator.next)
else:
    IMapIterator.__next__ = wrapper(IMapIterator.__next__)


# allow instance methods to be pickled.
# from Steven Bethard
# http://stackoverflow.com/questions/1816958/cant-pickle-type-instancemethod-when-using-pythons-multiprocessing-pool-ma
try:
    from copy_reg import pickle
except ImportError:
    from copyreg import pickle
from types import MethodType

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

pickle(MethodType, _pickle_method, _unpickle_method)

#def pool_sig():
#    signal.signal(signal.SIGINT, signal.SIG_IGN)

def pool(n=None, dummy=False):
    """
    create a multiprocessing pool that responds to interrupts.
    """

    if dummy:
        from multiprocessing.dummy import Pool
    else:
        from multiprocessing import Pool
    if n is None:
        import multiprocessing
        n = multiprocessing.cpu_count() - 1

    return Pool(n)


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

    # make it easier to debug.
    if n == 1:
        for r in it.starmap(f, iterable):
            yield r
        raise StopIteration


    if p is None:
        po = pool(n, dummy)
    else:
        po = p
    assert hasattr(po, 'imap')
    f = _func_star(f)

    try:
        for r in po.imap(f, iterable):
            yield r

    # explicitly clean up created pool
    finally:
        if p is None:
            try:
                po.close()
                po.join()
            except:
                pass
