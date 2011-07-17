Toolshed: Less Boiler-Plate
===========================

This is a collection of well-tested, simple modules and functions
that I use frequently

Files
-----

If all you have is a file with a header and you want to get a dictionary
for each row::

    >>> from toolshed import reader, header
    >>> for d in reader('src/toolshed/tests/data/file_data.txt'):
    ...    print d['a'], d['b'], d['c']
    1 2 3
    11 12 13
    21 22 23

works the same for gzipped and bzipped files and for stdin (via "-")::

    >>> for drow in (d for d in reader('src/toolshed/tests/data/file_data.txt.gz') if int(d['a']) > 10):
    ...    print drow['a'], drow['b'], drow['c']
    11 12 13
    21 22 23

sometimes you just want the header::

   >>> header('src/toolshed/tests/data/file_data.txt')
   ['a', 'b', 'c']

Shedskinner
-----------

Shedskin is a program that takes python scripts, infers the types based
on example input and generates fast C++ code that compiles to a python
extension module. Shedskinner is a decorator that automates this for a single
function. Use looks like::

    from toolshed import shedskinner

    @shedskinner((2, 12), long=True, fast_random=True):
    def adder(a, b):
        return a + b

Where here, we have decorated the adder function to make it a compiled, fast
version that accepts and returns integers. The (2, 12) are example arguments
to the function so that shedskin can infer types. 
The keyword arguments are sent to the compiler (see:
https://gist.github.com/1036972) for more examples.

Links
-----

- `Distribute`_
- `Buildout`_
- `modern-package-template`_

.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _`modern-package-template`: http://pypi.python.org/pypi/modern-package-template
