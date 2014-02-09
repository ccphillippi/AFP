'''
.. module:: helpers

Helper functions for cleaner

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import os
import errno

def ensurePath( filepath ):
    """
    Create a path if it doesn't not currently exist, else does nothing
    """
    try:
        os.makedirs( filepath )
    except OSError as e:
        if( e.errno == errno.EEXIST and os.path.isdir( filepath ) ): pass
        else: raise


def flatten( deepIterable ):
    """
    Flatten iterables of iterables of ... to list with depth of 1
    """
    if isinstance( deepIterable, str ):
        return [ deepIterable ];
    try:
        return [ a for i in deepIterable for a in flatten( i ) ]
    except:
        return [ deepIterable ]
