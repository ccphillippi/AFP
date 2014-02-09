'''
Created on Feb 8, 2014

@author: Christopher Phillippi
'''

from collections import Counter
from scipy import sparse
from itertools import izip

class WordCounterBase( object ):
    def __call__( self, articles ):
        counts, i, j = izip( *[ ( count, i, j ) 
                                            for i, article in enumerate( articles )
                                            for j, count in self.getCounts( article ) ] )
        return sparse.coo_matrix( ( counts, ( i, j ) ) ).tocsr()
    
    def getCounts( self, article ):
        raise NotImplemented


class WordCounter( WordCounterBase ):
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
