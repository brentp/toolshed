"""
def adder(a, b):
    return a + b

try:
    from toolshed import shedskinner


    adder_ss = shedskinner((4, 5))(adder)

    def test_adder():
        assert adder(2, 3)  == 5

    def test_adder_ss():
        assert adder_ss(2, 3)  == 5

    def teardown_func():
        import os
        import glob
        for f in glob.glob("shedskin*.py*"):
            os.unlink(f)
        for f in glob.glob("shedskin*.*pp"):
            os.unlink(f)
        for f in glob.glob("shedskin*.so"):
            os.unlink(f)
        for f in glob.glob("Makefile_*"):
            if len(f) > 20:
                os.unlink(f)

    test_adder_ss.teardown = teardown_func

except ImportError:
    pass
"""
