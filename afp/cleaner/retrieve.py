'''
.. module:: retrieve

High level API to retrieve cleaned files

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import cleaner.settings as settings
import csv
import os

def getCleanArticles( cleanStore ):
    """Returns iterable of all cleaned articles
    
    :param cleanStore: Absolute path to clean store
    """
    def getArticle( f ):
        with open( f, 'r' ) as opened:
            article = opened.read()
        return article
    return ( getArticle( f ) for f in getCleanFileList( cleanStore ) )

def getCleanFileList( cleanStore ):
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
    """Returns a table in structure of structure format ( Date By Ticker )
    
    :param tickerList: A list of the tickers to be added into the table
    :param fromDate: Time from which to begin the table
    :type fromDate: :py:class:`datetime.date`
    :param toDate: TIme from which to end the table
    :type toDate: :py:class:`datetime.date`
    :param empiricalStore: The location of the Empirical file store
    :param filename: The name of the file within the Empirical file store
    
    """
    def getPath():
        path = os.path.abspath( empiricalStore )
        return os.path.join( path, filename )
    begin = str( fromDate )
    end = str( toDate )
    with open( getPath(), 'r' ) as csvFile:
        csvReader = csv.DictReader( csvFile )
        empiricalTable = dict( ( row[ 'Date' ],
                                 dict( ( ( ticker, row[ ticker ] ) 
                                         for ticker in tickerList ) ) )
                               for row in csvReader
                               if row[ 'Date' ] >= begin and row[ 'Date' ] <= end )
    return empiricalTable
            
        
    
if __name__ == "__main__":
    files = getCleanFileList( settings.CLEAN_STORE )
    for f in files:
        print f
