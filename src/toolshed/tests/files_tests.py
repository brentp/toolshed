from toolshed.files import tokens, nopen, reader, header, is_newer_b,\
                            ProcessException
import os.path as op
import os
import glob
import time

DATA = op.join(op.dirname(__file__), "data")

def test_tokens():
    t = "asdf,2345,678"
    assert tokens(t, sep=",") == t.split(",")
    t = t.replace(",", "\t")
    assert tokens(t) == t.split("\t")

def test_is_newer():

    open('tt.tmp', 'w').close()
    time.sleep(0.5)
    open('uu.tmp', 'w').close()
    assert not is_newer_b('uu.tmp', 'tt.tmp')
    time.sleep(0.5)
    open('tt.tmp', 'w').close()
    os.unlink('tt.tmp')
    os.unlink('uu.tmp')

from nose.tools import raises

@raises(ProcessException)
def test_nopen_raises():
    nopen("|asdfasdfasdfasdfasdf").next()

def test_nopen():
    lines = open(op.join(DATA, "file_data.txt")).readlines()
    for f in glob.glob(op.join(DATA, "*")) + [lines,
        "http://www.stanford.edu/class/stats191/data/salary.table"]:
        yield check_nopen, f
        yield check_reader, f
        yield check_ordered_reader, f
        yield check_reader_no_header, f
        yield check_header, f
    line_iter = open(op.join(DATA, "file_data.txt"))

    for fn in (check_nopen, check_reader, check_reader_no_header,
            check_header):
        line_iter.seek(0)
        yield fn, line_iter

def check_header(fname):
    assert isinstance(header(fname), list)

def check_nopen(fname):
    d = nopen(fname)
    assert hasattr(d, "__iter__")

def check_reader(fname):
    if not "http:" in fname:
        for d in reader(fname):
            assert all((k in d for k in "abc"))
            assert d['a']
    else:
        for d in reader(fname):
            assert all((k in d for k in "SXEM"))

def check_ordered_reader(fname):
    if not "http:" in fname:
        for d in reader(fname, header="ordered"):
            assert all((k in d for k in "abc"))
            d["0"] = "extra"
            d["_"] = "other"
            assert d.keys() == ["a", "b", "c", "0", "_"]

def check_reader_no_header(fname):
    for l in reader(fname, header=False):
        assert isinstance(l, list)

