'''
Created on Feb 7, 2014

@author: Christopher Phillippi
'''

from collections import Counter
from itertools import izip
from scipy import sparse
import cleaner
import afp

def countBy( wordCounter, articles ):
    ij, count = izip( *( ( ( i, j ), count ) 
                           for i, article in enumerate( articles )
                           for j, count in wordCounter.getCounts( article ) ) )
    return sparse.csc_matrix( count, ij )

class WordCounterBase( object ):
    def getCounts( self, article ):
        raise NotImplemented

class WordCounter( object ):
    def __init__( self, keywordsToIndices ):
        self.keywordsToIndices = keywordsToIndices
        
    def getCounts( self, article ):
        afp.keywords = ( self.keywordsToIndices[ keyword ]  
                     for keyword in article 
                     if keyword in self.keywordsToIndices )
        return Counter( afp.keywords ).iteritems()
        
# def buildCovariance( files, keywords ):
#    return tfIdf( wordCounts( files, keywords ) )

if __name__ == "__main__":
    articles = cleaner.retrieve.getCleanArticles( cleaner.settings.CLEAN_STORE )
    afp.keywords = afp.keywords.getAliasToKeywordMap( afp.settings.KEYWORDS_FILEPATH )
    # tfidf = NormalizeBy( TfIdf() )( CountBy( WordCounter( keywords ) )( articles ) )
