from toolshed.files import tokens, nopen, reader
import os.path as op
import glob

DATA = op.join(op.dirname(__file__), "data")

def test_tokens():
    t = "asdf,2345,678"
    assert tokens(t, sep=",") == t.split(",")
    t = t.replace(",", "\t")
    assert tokens(t) == t.split("\t")

def test_nopen():
    lines = open(op.join(DATA, "file_data.txt")).readlines()
    line_iter = open(op.join(DATA, "file_data.txt"))
    for f in glob.glob(op.join(DATA, "*")) + [lines, line_iter]:
        yield check_nopen, f
        yield check_reader, f
        yield check_reader_no_header, f

def check_nopen(fname):
    d = nopen(fname)
    assert hasattr(d, "__iter__")

def check_reader(fname):
    for d in reader(fname):
        assert all((k in d for k in "abc"))
        assert d['a']

def check_reader_no_header(fname):
    for l in reader(fname, header=False):
        assert isinstance(l, list)

