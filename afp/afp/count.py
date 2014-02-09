'''
.. module:: count

This module contains the functors which count the keywords in a set of articles, producing a matrix

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

from collections import Counter
from scipy import sparse
from itertools import izip

class WordCounterBase( object ):
    """Base class for WordCounter Functors
    
    Extending Requires method: **getCounts()**
    """
    def __call__( self, articles ):
        counts, i, j = izip( *[ ( count, i, j ) 
                                            for i, article in enumerate( articles )
                                            for j, count in self.getCounts( article ) ] )
        return sparse.coo_matrix( ( counts, ( i, j ) ) ).tocsr()
    
    def getCounts( self, article ):
        """Required to be a WordCounter, must be implemented in extending class.
        """
        raise NotImplemented


class WordCounter( WordCounterBase ):
    """Functor that counts all keywords in keywordsToIndices map in an article.
    
    Returns: Sparse matrix of counts with articles on rows and words on columns from scipy.sparse.csr_matrix
    
    Example usage:
    
    >>> articles = retrieve.getCleanArticles( cleanersettings.CLEAN_STORE )
    >>> keywordsToIndices = keywords.getKeywordToIndexMap( settings.KEYWORDS_FILEPATH )
    >>> countMatrix = count.WordCounter( keywordsToIndices )( articles )
    >>> countMatrix
    (0, 7)     3
    (0, 35)    2
    (0, 48)    1
    (1, 7)     2
    ...
    
    """
    import afp.normalize as normalize
    _articleNormalizer = normalize.Article()
    
    def __init__( self, keywordsToIndices ):
        self.keywordsToIndices = keywordsToIndices
        
    def getCounts( self, article ):
        def getKeywords():
            return ( self.keywordsToIndices[ keyword ]
                     for keyword in self._articleNormalizer( article )
                     if keyword in self.keywordsToIndices )
        return Counter( getKeywords() ).iteritems()
    
