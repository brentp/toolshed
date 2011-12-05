
import sys
import subprocess as sp

def sh(cmd, log=sys.stderr, wait=False):
    r"""
    >>> sh('echo "hi"').stdout.read()
    'hi\n'
    >>> sh('echo "hi"', wait=True)
    <subprocess.Popen object ...>
    """
    log.write("[running command] %s\n" % cmd)
    p = sp.Popen(cmd, shell=True, stderr=sp.PIPE, stdout=sp.PIPE)
    if wait:
        for line in p.stderr:
            print >>log, line,
        p.wait()
        if p.returncode != 0:
            sys.exit(p.returncode)
    return p

if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                               doctest.NORMALIZE_WHITESPACE)
