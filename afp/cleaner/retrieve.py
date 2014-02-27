'''
.. module:: retrieve

High level API to retrieve cleaned files

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import cleaner.settings as settings
import csv
import os
import os.path
import pandas as pd

def getArticles( fileList ):
    def getArticle( f ):
        with open( f, 'r' ) as opened:
            article = opened.read()
        return article
    return ( getArticle( f ) for f in fileList )

def getCleanArticles( cleanStore = settings.CLEAN_STORE ):
    """Returns iterable of all cleaned articles
    
    :param cleanStore: Absolute path to clean store
    """
    return getArticles( getCleanFileList( cleanStore ) )

def getDailyArticles( date, cleanStore = settings.CLEAN_STORE ):
    return getArticles( getDailyFileList( cleanStore ) )

def getDailyFileList( date, cleanStore = settings.CLEAN_STORE ):
    pass

def getFilteredFileList( includes = None,
                         excludes = None,
                         cleanStore = settings.CLEAN_STORE ):
    def getFileListAtDepth( depth ):
        directory = ( os.path.join( cleanStore, f ) for f in os.listdir( cleanStore ) )
        for f in directory:
            if os.path.isfile( f ):
                yield f
            else:
                for subFile in getCleanFileList( f ):
                    yield subFile
    return getFileListAtDepth( 0 )
    
    

def getCleanFileList( cleanStore = settings.CLEAN_STORE ):
    """Returns interable of all cleaned files
    
    :param cleanStore: Absolute path to clean store
    """    
    directory = ( os.path.join( cleanStore, f ) for f in os.listdir( cleanStore ) )
    for f in directory:
        if os.path.isfile( f ):
            yield f
        else:
            for subFile in getCleanFileList( f ):
                yield subFile

def getEmpiricalTable( tickerList, 
                       fromDate, 
                       toDate, 
                       empiricalStore = settings.EMPIRICAL_STORE, 
                       filename = settings.ADJUSTED_CLOSE_FILENAME ):
    """Returns a table in structure of structure format ( Ticker By Date )
    
    :param tickerList: A list of the tickers to be added into the table
    :param fromDate: Time from which to begin the table
    :type fromDate: :py:class:`datetime.date`
    :param toDate: TIme from which to end the table
    :type toDate: :py:class:`datetime.date`
    :param empiricalStore: The location of the Empirical file store
    :param filename: The name of the file within the Empirical file store
    
    """
    begin = str( fromDate )
    end = str( toDate )
    with open( _getPath( empiricalStore, filename ), 'r' ) as csvFile:
        csvReader = csv.DictReader( csvFile )
        empiricalTable = dict( ( row[ 'Date' ],
                                 dict( ( ( ticker, row[ ticker ] ) 
                                         for ticker in tickerList ) ) )
                               for row in csvReader
                               if row[ 'Date' ] >= begin and row[ 'Date' ] <= end )
        
    return empiricalTable
            
def getEmpiricalDataFrame( tickerList, 
                           fromDate, 
                           toDate, 
                           empiricalStore = settings.EMPIRICAL_STORE, 
                           filename = settings.ADJUSTED_CLOSE_FILENAME ):
    """Returns a :py:class:`pandas.DataFrame` according to selected stocks and dates
    
    :param tickerList: A list of the tickers to be added into the table
    :param fromDate: Time from which to begin the table
    :type fromDate: :py:class:`datetime.date`
    :param toDate: TIme from which to end the table
    :type toDate: :py:class:`datetime.date`
    :param empiricalStore: The location of the Empirical file store
    :param filename: The name of the file within the Empirical file store
    
    """ 
    df = pd.read_csv( _getPath( empiricalStore, filename ), index_col = 0, parse_dates = True )
    tickers = set( tickerList )
    extraColumns = [ column for column in df.columns if column not in tickers ]
    start = df.index.searchsorted( fromDate )
    end = df.index.searchsorted( toDate )
    return df[ start:end ].drop( extraColumns, 1 )

def getTfIdfDataFrame( empiricalDataFrame ):
    pass
    
def _getPath( empiricalStore, filename ):
    path = os.path.abspath( empiricalStore )
    return os.path.join( path, filename )
    
    
if __name__ == "__main__":
    files = getCleanFileList( settings.CLEAN_STORE )
    for f in files:
        print f
