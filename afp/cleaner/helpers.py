'''
Created on Feb 7, 2014

@author: Christopher Phillippi
@summary: Helper functions for cleaner
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


def flatten( x ):
    """
    Flatten iterables of iterables of ... to list with depth of 1
    """
    if isinstance( x, str ):
        return [ x ];
    try:
        return [ a for i in x for a in flatten( i ) ]
    except:
        return [ x ]
