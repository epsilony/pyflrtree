from flrtree.flrtree import LRTree

def test(verbose=False):
    import os, nose

    # find the directory where the test package lives
    from flrtree import tests
    dir = os.path.dirname( tests.__file__ )

    # get the name of the test package
    argv = [ 'nosetests', '--exe', dir ]

    # run nose
    try :
        return nose.main( argv = argv )
    except SystemExit as e :
        return e.code

__all__ = ['LRTree','test']
