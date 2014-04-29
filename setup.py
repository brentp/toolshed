import os
import sys

# HACK to prevent 'atexit' error in 'nose.collector'. See issues for
# details https://github.com/travis-ci/travis-ci/issues/1778
import multiprocessing

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


# from mpld3
def get_version():
    """Get the version info from the mpld3 package without importing it"""
    import ast

    with open(os.path.join("toolshed", "__init__.py"), "r") as init_file:
        module = ast.parse(init_file.read())

    version = (ast.literal_eval(node.value) for node in ast.walk(module)
               if isinstance(node, ast.Assign)
               and node.targets[0].id == "__version__")
    try:
        return next(version)
    except StopIteration:
        raise ValueError("version could not be located")


tests_require = ["nose"]

if sys.version_info[:2] < (2, 7):
    install_requires = ["argparse", "ordereddict"]
else:
    install_requires =   []


setup(name='toolshed',
    version=get_version(),
    description="Tools for data",
    long_description=README,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      'Topic :: Scientific/Engineering',
      'Topic :: Scientific/Engineering :: Bio-Informatics',
      'Topic :: Text Processing',
      'Topic :: Utilities',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 3'
    ],
    keywords='bioinformatics',
    author='Brent Pedersen',
    author_email='bpederse@gmail.com',
    url='https://github.com/brentp/toolshed/',
    license='BSD (2-clause)',
    packages=['toolshed'],
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=tests_require,
    install_requires=install_requires,
    entry_points={'console_scripts': ['toolshed=toolshed:main']}
)
