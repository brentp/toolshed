from files import reader, tokens, nopen
import sys

try:
    from optimize import shedskinner
except ImportError:
    pass


def main():
    #import argparse
    #p = argparse.ArgumentParser(__doc__)
    pass


if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE).failed == 0:
        main()

