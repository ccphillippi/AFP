'''
Created on Feb 8, 2014

@author: Christopher Phillippi
'''

from collections import Counter
from scipy import sparse
from itertools import izip

class WordCounterBase( object ):
    def __call__( self, articles ):
        ij, count = izip( *( ( ( i, j ), count ) 
                               for i, article in enumerate( articles )
                               for j, count in self.getCounts( article ) ) )
        return sparse.csc_matrix( count, ij )
    
    def getCounts( self, article ):
        raise NotImplemented


class WordCounter( WordCounterBase ):
    def __init__( self, keywordsToIndices ):
        self.keywordsToIndices = keywordsToIndices
        
    def getCounts( self, article ):
        keywords = ( self.keywordsToIndices[ keyword ]  
                     for keyword in article.lower() 
                     if keyword in self.keywordsToIndices )
        return Counter( keywords ).iteritems()
