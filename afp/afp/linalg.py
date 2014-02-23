'''
.. module:: linalg

This module contains the sparse matrix operations required for processing that do not reside in scipy/numpy 

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import numpy as np

def cov( sparse, isSample = True ):
    """Computes a covariance matrix for very large sparse matrices with small memory overhead. If
    speed is of upmost concern, just use :py:func:`numpy.cov`.
    
    :param sparse: Sparse matrix ( m x n )
    :type sparse: :py:func:`scipy.sparse.csr_matrix` or similar sparse matrix
    """
    n = sparse.shape[ 0 ]
    def sumOuterProducts( outer, row ):
        return outer + np.outer( row.T, row )
    mu = ( 1.0 / n ) * sum( sparse ).todense()
    return reduce( sumOuterProducts, ( sparse.getrow( i ) - mu for i in xrange( n ) ), 0 ) / ( n - isSample )

def corr( sparse, isSample = True ):
    """Computes a correlation matrix for very large sparse matrices with small memory overhead. If
    speed is of upmost concern, just use :py:func:`numpy.corrcoef`.
    
    :param sparse: Sparse matrix ( m x n )
    :type sparse: :py:func:`scipy.sparse.csr_matrix` or similar sparse matrix
    """
    covMat = cov( sparse, isSample )
    invsd = 1.0 / np.sqrt( np.diag( covMat ) )
    return covMat * np.outer( invsd.T, invsd )
    
if __name__ == "__main__":
    pass
