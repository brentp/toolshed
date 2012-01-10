from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1.5'

install_requires = [
    'nose',
]


setup(name='toolshed',
    version=version,
    description="Tools for data",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      'Topic :: Scientific/Engineering',
      'Topic :: Scientific/Engineering :: Bio-Informatics',
      'Topic :: Text Processing',
      'Topic :: Utilities'
    ],
    keywords='bioinformatics',
    author='Brent Pedersen',
    author_email='bpederse@gmail.com',
    url='https://github.com/brentp/toolshed/',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['toolshed=toolshed:main']
    }
)
