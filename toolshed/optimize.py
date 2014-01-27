import os.path as op
import sys
from shedskin import setgx, newgx, getgx, infer, annotate, cpp, shared
import inspect
import hashlib
import subprocess

class shedskinner(object):
    r"""
    decorator to shedskin-ify functions.
    and example is::

        @shedskinner((2, 4), (6, 12), long=True, random=True, wrap_around_check=False)
        def adder(a, b):
            return a + b


        print(adder(6, 8))

    note the decorator is called with example invocations so that
    shedskin can infer types. After the first invocation, the extension
    module is stored so that subsequent calls will run quickly.

    If either the function or the decorator is changed, a new module
    will be recreated.

    Parts of this were written by: https://gist.github.com/fahhem
    """
    kwlookup = {
            'nobounds': 'bounds_checking',
            'long': 'longlong',
            'nowrap': 'wrap_around_check',
            'random': 'fast_random',
            'strhash': 'fast_hash',
            }

    def __init__(self, *invocations, **kwargs):
        self.modules = kwargs.pop('modules',())
        self.functions = kwargs.pop('functions',())
        self.kwargs = kwargs

        self.invocations = invocations

    def _hash(self, source):
        return hashlib.md5(source).hexdigest()

    def _tmp(self, source_hash, ext=".py"):
        return "shedskin" + source_hash + ext

    def _get_function_source(self, fn):
        if isinstance(fn, basestring):
            fn = globals()[fn]
        src = inspect.getsource(fn)
        return src


    def __call__(self, fn):
        setgx(newgx())
        # set kwargs from the __init__ call.
        for k, v in self.kwargs.items():
            k = shedskinner.kwlookup.get(k, k)
            setattr(getgx(), k, v)
        getgx().annotation = True
        getgx().extension_module = True

        src = self._get_function_source(fn)
        source_hash = self._hash(src)
        if self._is_up_to_date(source_hash):
            mod = self._get_module(self._tmp(source_hash))
            return getattr(mod, fn.func_name)

        tmp = open(self._tmp(source_hash), "w")
        for mod in self.modules:
            if hasattr(mod, "__module__"):
                tmp.write('from %s import %s\n' % (mod.__module__,mod.__name__))
                continue
            elif hasattr(mod, "__name__"):
                mod = mod.__name__
            tmp.write('import %s\n' % mod)

        for other_fn in self.functions:
            tmp.write(self._get_function_source(other_fn) + '\n')

        # hack to get the function source without the decorator line...
        # needs to be fixed...
        if src[0] == "@":
            tmp.write(src.split('\n', 1)[1] + '\n')
        else:
            tmp.write(src + '\n')
        for i in self.invocations:
            tmp.write("%s%s\n" % (fn.func_name, str(i)))
        tmp.close()

        makefile = getgx().makefile_name = "Makefile_%s" % source_hash
        self._run_shedskin(tmp.name, makefile)
        mod = self._get_module(tmp.name)
        return getattr(mod, fn.func_name)

    def _is_up_to_date(self, source_hash):
        return op.exists(self._tmp(source_hash, ext=".so"))

    def _run_shedskin(self, name, makefile):
        old = sys.stdout
        log = sys.stdout = open(name + ".log", "w")
        getgx().main_mod = name[:-3]
        infer.analyze(name)
        annotate.annotate()
        cpp.generate_code()
        shared.print_errors()
        ret = subprocess.call("make -f %s" % makefile, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log.close()
        sys.stdout = old
        if ret != 0:
            sys.stderr.write("error making %s\n" % makefile)
            print(open(log.name).read())

    def _get_module(self, name):
        if name.endswith(".py"):
            name = name[:-3]
        mod = __import__(name)
        return mod
