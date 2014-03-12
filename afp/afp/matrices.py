'''
.. module:: matrices

This module contains the matrix generating functions

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''
from __future__ import print_function

from os.path import join
import cleaner.retrieve as retrieve
import cleaner.helpers as helpers
import keywords
import count
import normalize
import settings
import sentiment
import cPickle
import datetime
import numpy as np
import pandas as pd
import scipy.sparse as sparse
   
def tfIdf( articles, keywordsFilePath = settings.KEYWORDS_FILEPATH ):
    """Returns a sparse tf-idf Matrix
    
    :param articles: An iterable of article strings. See :func:`cleaner.retrieve.getCleanArticles`
    :param keywordsFilePath: Path to *keywords.csv*
    :type keywordsFilePath: str
    """
    keywordMap = keywords.getKeywordToIndexMap( keywordsFilePath );
    counts = count.WordCounter( keywordMap )( articles )
    return normalize.TfIdf()( counts )

def getEmpiricalDataFrame( tickerList,
                           fromDate,
                           toDate,
                           csvPath = retrieve.adjustedClosesFilepath() ):
    """Returns a :py:class:`pandas.DataFrame` according to selected stocks and dates
    
    :param tickerList: A list of the tickers to be added into the table
    :param fromDate: Time from which to begin the table
    :type fromDate: :py:class:`datetime.date`
    :param toDate: TIme from which to end the table
    :type toDate: :py:class:`datetime.date`
    :param csvPath: The name of the file within the Empirical file store
    
    """ 
    df = pd.read_csv( csvPath, index_col = 0, parse_dates = True )
    tickers = set( tickerList )
    extraColumns = [ column for column in df.columns if column not in tickers ]
    start = df.index.searchsorted( fromDate )
    end = df.index.searchsorted( toDate )
    return df[ start:end ].drop( extraColumns, 1 )

def getCountDataFrame( tickerList,
                       wordCounter,
                       dates,
                       aggregator = None,
                       loadCache = True,
                       saveCache = False ):
    def cache( countDf, hashCode ):
        path = join( settings.CACHE_DIR, str( hashCode ) + '.pkl' )
        helpers.ensurePath( settings.CACHE_DIR )
        with open( path, 'wb' ) as f:
            print( 'Caching...', end = '' )
            cPickle.dump( countDf, f, -1 )
            print( 'Cached' )
            
    query = ( tuple( tickerList ),
              helpers.tryexcept( lambda: tuple( dates ), dates ),
              helpers.tryexcept( lambda: aggregator.__name__, aggregator ),
              str( type( wordCounter ) ) )
    hashCode = query.__hash__()
    if loadCache:
        try:
            with open( join( settings.CACHE_DIR, str( hashCode ) + '.pkl' ), 'rb' ) as f:
                cachedCounts = cPickle.load( f )
            return cachedCounts
        except TypeError:
            print( 'Could not hash query:', query )
        except IOError:
            print( 'Cache does not exist for count query:', query )
            if aggregator != None:
                print( 'Checking for non-aggregated cache..' )
                altQuery = ( tuple( tickerList ),
                             helpers.tryexcept( lambda: tuple( dates ), dates ),
                             None,
                             str( type( wordCounter ) ) )
                try:
                    with open( join( settings.CACHE_DIR, str( altQuery.__hash__() ) + '.pkl' ), 'rb' ) as f:
                        rawCounts = cPickle.load( f )
                    countDf = rawCounts.to_dense().groupby( level = 0 ).apply( aggregator ).to_sparse( 0 )
                    cache( countDf, hashCode )
                    return countDf
                except IOError:
                    print( 'No non-aggregated cache' )
                    print( 'Calculating from filesystem...' )
                
    
    def getCountMatrix():
        params = ( ( date, aggregator, wordCounter ) 
                   for date in dates )
        datesRows = ( _getCountRows( args ) for args in params )           
        allDates, counts = zip( *( ( date, row ) 
                                   for date, matrix in datesRows
                                   for row in matrix
                                   if row.nnz ) )
        return ( allDates, sparse.vstack( counts ).tocsr() )
    allDates, counts = getCountMatrix()
    countDf = sparseToDataFrame( counts, allDates, tickerList )
    if saveCache or loadCache:
        cache( countDf, hashCode )
    return countDf

def getTfIdfDataFrame( wordCounter, dates, aggregator = None ):
    return normalize.TfIdf()( getCountDataFrame( wordCounter, dates, aggregator ) )
    
def sparseToDataFrame( sparseMat, index, columns ):
    return pd.SparseDataFrame( [ pd.SparseSeries( sparseMat[i].toarray().ravel() ) 
                                 for i in np.arange( sparseMat.shape[0] ) ],
                               index = index,
                               columns = columns,
                               default_fill_value = 0 )

def _getCountRows( args ):
    timestamp, aggregator, wordCounter = args
    try:
        date = timestamp.date()
    except AttributeError:
        date = timestamp
    counts = wordCounter( retrieve.getDailyArticles( date ) )
    try:
        return ( date, aggregator( counts ) )
    except TypeError:
        return ( date, counts )
    
if __name__ == "__main__":    
    begin = datetime.date( 2011, 1, 3 )
    end = datetime.date( 2013, 11, 27 )
    tickerList = keywords.getTickerList()
    keywordsMap = keywords.getKeywordToIndexMap()
    empiricalDf = getEmpiricalDataFrame( tickerList, begin, end )
    countDf = getCountDataFrame( tickerList,
                                 count.SentimentWordCounter( keywordsMap,
                                                             sentiment.classifier() ),
                                 empiricalDf.index,
                                 aggregator = np.sum )
    tfidf = normalize.TfIdf()( countDf )
    empiricalDf = empiricalDf.ix[ tfidf.index ]
    tfidf.to_dense().to_csv( join( settings.RESULTS_DIR, 'tfidf_sentimentMatched.csv' ) )
    empiricalDf.to_dense().to_csv( join( settings.RESULTS_DIR, 'empiricalMatched.csv' ) )
    # corr.to_csv( join( settings.RESULTS_DIR, 'corrtest_withSent_all.csv' ) )
