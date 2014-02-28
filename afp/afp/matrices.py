'''
.. module:: matrices

This module contains the matrix generating functions

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import cleaner.retrieve as retrieve
import afp.keywords as keywords
import afp.count as count
import afp.normalize as normalize
import afp.settings as settings
import datetime
import numpy as np
import scipy.sparse as sparse
import pandas as pd
   
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

def getCountDataFrame( tickerList, dates, aggregator = None ):
    wordCounter = count.WordCounter( keywords.getKeywordToIndexMap() )  # TODO: get from ticker list
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
    allDates, Counts = getCountMatrix()
    return sparseToDataFrame( Counts, allDates, tickerList )

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
    end = datetime.date( 2013, 11, 1 )
    tickerList = keywords.getTickerList()
    empiricalDf = getEmpiricalDataFrame( tickerList, begin, end )
    countDf = getCountDataFrame( tickerList, empiricalDf.index )
    print normalize.TfIdf()( countDf )
    # corr = linalg.corr( tfIdf( retrieve.getCleanArticles() ) )
    # np.savetxt( settings.RESULTS_DIR + '/corr2012.csv', corr, delimiter = ',' )
