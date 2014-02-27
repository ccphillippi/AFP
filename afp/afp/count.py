'''
.. module:: count

This module contains the functors which count the keywords in a set of articles, producing a matrix

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

from collections import Counter
from scipy import sparse
from itertools import izip
from itertools import groupby
import math

class WordCounterBase( object ):
    """Base class for WordCounter Functors
    
    Extending requires method: **getCounts()**
    """
    def __call__( self, articles ):
        """Returns a sparse ( **m** x **n** ) matrix of word counts for **m** articles and **n** assets
        """
        counts, i, j = izip( *[ ( count, i, j ) 
                                            for i, article in enumerate( articles )
                                            for j, count in self.getCounts( article ) ] )
        return sparse.coo_matrix( ( counts, ( i, j ) ) ).tocsr()
    
    def getCounts( self, article ):
        """Returns a list of 2-tuples where the first element of each tuple corresponds to the asset's index
        and the second element corresponds to the assets count within the article.
        
        :param article: An article to count a list of asset counts for
        :type article: :py:class:`str`
        
        """
        raise NotImplemented
    
class SentimentCounterBase( object ):
    """Base class for SentimentCounter Functors
    
    Extending requires method: **getCount()** which summarizes sentiment values for a given stock into a single scalar statistic
    """
    def __call__( self, sentimentPairs ):
        """Reduces a list of ( index, sentiment ) pairs to a dictionary of unique indices and aggregated sentiment
        
        *Note: aggregated sentiment calculation depends on inheriting SentimentCounter's getCount method* 
        
        :param sentimentPairs: ( key, value ) pairs where the key is the index of the keyword, and value is the sentiment of the keyword
        :type sentimentPairs: iterable of :py:class:`tuple`
        
        [ ( index0, sentiment0 ), ( index1, sentiment1 ), ( index0, sentiment2 ) ] --> [ ( index0, aggregateSent0 ), ( index1, aggregateSent1 ) ]
        """
        def assetKey( pair ): return pair[ 0 ]
        def sentiments( pairList ): return [ sentiment for _, sentiment in pairList ]
        def sign( x ): return math.copysign( 1, x ) 
        def getCount( sentimentList ): return sign( sum( sentimentList ) ) * len( sentimentList )
        
        sortedPairs = sorted( sentimentPairs, key = assetKey )
        return dict( ( i, getCount( sentiments( pairList ) ) ) for i, pairList in groupby( sortedPairs, assetKey ) )
    
    def getCount( self, sentiments ):
        """Returns the aggregate sentiment calculation for all sentiments
        
        **MUST be implemented in base class**
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
        """
        :param keywordsToIndices: Maps keywords to their index within a count matrix
        :type keywordsToIndices: :py:class:`dict`
        """
        self.keywordsToIndices = keywordsToIndices
        
    def getCounts( self, article ):
        """Returns a list of 2-tuples where the first element of each tuple corresponds to the asset's index
        and the second element corresponds to the assets count within the article.
        
        :param article: An article to count a list of asset counts for
        :type article: :py:class:`str`
        
        :returns: iterable of tuples with the first value corresponding to the keyword index, and the second value corresponding to the count
        :rtype: generator expression
        """
        def getKeywords():
            return ( self.keywordsToIndices[ keyword ]
                     for keyword in self._articleNormalizer( article )
                     if keyword in self.keywordsToIndices )
        return Counter( getKeywords() ).iteritems()
    
class SentimentCounter( SentimentCounterBase ):
    """Reduces a list of ( index, sentiment ) pairs to a dictionary of unique indices and aggregated sentiment
    
    Example usage:
    
    >>> import afp.count as count
    >>> sentimentPairs = ( ( \'GOOG\', -1 ), ( \'AAPL\', 1 ), ( \'GOOG\', -1 ), ( \'GOOG\', 1 ) )
    >>> count.SentimentCounter()( sentimentPairs )
    {\'GOOG\': -3.0, \'AAPL\': 1.0}
    
    """
    def getCount( self, sentimentList ):
        """Returns the aggregate sentiment calculation for all sentiments
        
        The *sign* of the count is the same as the net sentiment. Net 0 sentiment results in a positive sign.
        
        The *magnitude* of the count is the number of occurrences.
        
        :param sentimentList: Sentiment readings from classifier
        :type sentimentList: :py:func:`list`
        :returns: sign( Net Sentiment ) *x* ( Number of occurrences )
        :rtype: :py:class:`float` 
        
        """
        def sign( x ): return math.copysign( 1, x ) 
        return sign( sum( sentimentList ) ) * len( sentimentList )
    
