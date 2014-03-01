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

def getCountDataFrame( wordCounter,
                       dates,
                       aggregator = None,
                       loadCache = True,
                       saveCache = False ):
    if loadCache:
        try:
            query = ( tuple( tickerList ),
                      helpers.tryexcept( lambda: tuple( dates ), dates ),
                      helpers.tryexcept( lambda: tuple( aggregator ), aggregator ),
                      type( wordCounter ) )
            with open( join( settings.CACHE_DIR, str( query.__hash__() ) + '.pkl' ), 'rb' ) as f:
                cachedCounts = cPickle.load( f )
            return cachedCounts
        except TypeError:
            print( 'Could not hash query:', query )
        except IOError:
            print( 'Cache does not exist for count query:', query )
            print( 'Calculating from filesystem...' )
    
       
    def getCountMatrix():
        def getCountRows( timestamp ):
            counts = wordCounter( retrieve.getDailyArticles( timestamp.date() ) )
            try:
                return aggregator( counts )
            except TypeError:
                return counts            
        allDates, counts = zip( *( ( date, countRow ) 
                                   for date in dates
                                   for countRow in getCountRows( date )
                                   if countRow.nnz ) )
        return ( allDates, sparse.vstack( counts ).tocsr() )
    allDates, counts = getCountMatrix()
    countDf = sparseToDataFrame( counts, allDates, tickerList )
    if saveCache or loadCache:
        path = join( settings.CACHE_DIR, str( query.__hash__() ) + '.pkl' )
        helpers.ensurePath( settings.CACHE_DIR )
        with open( path, 'wb' ) as f:
            print( 'Caching...', end='' )
            cPickle.dump( countDf, f, -1 )
            print( 'Cached' )
    return countDf

def getTfIdfDataFrame( tickerList, dates, aggregator = None ):
    return normalize.TfIdf()( getCountDataFrame( tickerList, dates, aggregator ) )
    
def sparseToDataFrame( sparseMat, index, columns ):
    return pd.SparseDataFrame( [ pd.SparseSeries( sparseMat[i].toarray().ravel() ) 
                                 for i in np.arange( sparseMat.shape[0] ) ],
                               index = index,
                               columns = columns,
                               default_fill_value = 0 )
if __name__ == "__main__":    
    begin = datetime.date( 2011, 1, 3 )
    end = datetime.date( 2013, 11, 27 )
    tickerList = keywords.getTickerList()
    keywordsMap = keywords.getKeywordToIndexMap()
    empiricalDf = getEmpiricalDataFrame( tickerList, begin, end )
    countDf = getCountDataFrame( count.WordCounter( keywordsMap ),
                                 empiricalDf.index,
                                 aggregator = sum )
    corr = normalize.TfIdf()( countDf ).corr().to_dense()[ tickerList ]
    corr.to_csv( join( settings.RESULTS_DIR, 'corr2011_2013.csv' ) )
