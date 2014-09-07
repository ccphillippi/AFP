'''
.. module:: retrieve

High level API to retrieve cleaned files

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

from itertools import chain
from os import listdir
import cleaner.settings as settings
import cleaner.schema as schema
import csv
import datetime
import os.path
    
def _getPath( store, filename ):
    path = os.path.abspath( store )
    return os.path.join( path, filename )
    
def adjustedClosesFilepath( empiricalStore = settings.EMPIRICAL_STORE,
                            filename = settings.ADJUSTED_CLOSE_FILENAME ):
    return _getPath( empiricalStore, filename )

def benchmarkFilepath():
    return adjustedClosesFilepath( empiricalStore = settings.EMPIRICAL_STORE,
                                   filename = 'benchmarks.csv' )
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
    return getArticles( getDailyFileList( date, cleanStore ) )

def getDailyFileList( date, store = settings.CLEAN_STORE, mergeWeekendsWithMonday = False ):
    
    fileList = getFilteredFileList( store = store,
                                    includes = { schema.YEAR  : [ str( date.year ) ],
                                                 schema.DAY   : [ str( date.day ) ],
                                                 schema.MONTH : [ date.strftime( '%B' ) ],
                                                } )
    if ( mergeWeekendsWithMonday and date.weekday == 0 ):
        return chain( fileList,
                      getDailyFileList( date - datetime.timedelta( days = 1 ),
                                        store,
                                        mergeWeekendsWithMonday ) )
    else:
        return fileList

def getFilteredFileList( includes = None,
                         excludes = None,
                         store = settings.CLEAN_STORE ):
    """Returns a list of files, based on includes and excludes filters
    
    :param includes: Dictionary of values to be included by schema category
    :type includes: :py:class:`dict`
    :param excludes: Dictionary of values to be excluded by schema category
    :type excludes: :py:class:`dict`
    
    Example Usage: (Assume you want all February articles in 2011 that are not in the NYT)
    
    >>> import cleaner.retrieve as retrieve
    >>> retrieve.getFilteredFileList( includes = { \'month\' : [ \'February\' ], \'year\' : [ \'2011\' ] }, excludes = { \'paper\' = [ \'New York Times\' ] } )
    ~\\AFPCorpus\\LexisNexis\\2011\\February\\1\\New York Times\\40_UNDER_FORTY_Financial_advi.txt
    ~\\AFPCorpus\\LexisNexis\\2011\\February\\1\\New York Times\\Walker_in_three_way_battle_for.txt
    ~\\AFPCorpus\\LexisNexis\\2011\\February\\2\\New York Times\\Clinton_to_Grace_This_Day_Awar.txt
    ...
    
    """
    def getFileListAtDepth( root, depth ):
        try:
            storeTag = schema.STORE_ORDER[ depth ]
        except IndexError:
            storeTag = "other"
        for f in os.listdir( root ):
            path = os.path.join( root, f )
            if os.path.isfile( path ):
                yield path
            else:
                try:
                    if f not in includes[ storeTag ]:
                        continue
                except KeyError:  # No specification for folder, assume included
                    pass
                except TypeError:  # includes is None
                    pass
                try:
                    if f in excludes[ storeTag ]:
                        continue
                except KeyError:  # No specification, assume included
                    pass
                except TypeError:  # excludes is None
                    pass
                for subFile in getFileListAtDepth( path, depth + 1 ):
                    yield subFile
    return getFileListAtDepth( store , 0 )
    

def getCleanFileList( cleanStore = settings.CLEAN_STORE ):
    """Returns interable of all cleaned files
    
    :param cleanStore: Absolute path to clean store
    """    
    directory = ( os.path.join( cleanStore, f ) for f in listdir( cleanStore ) )
    for f in directory:
        if os.path.isfile( f ):
            yield f
        else:
            for subFile in getCleanFileList( f ):
                yield subFile

def getEmpiricalTable( tickerList,
                       fromDate,
                       toDate,
                       csvFile = adjustedClosesFilepath() ):
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
    with open( csvFile, 'r' ) as csvFile:
        csvReader = csv.DictReader( csvFile )
        empiricalTable = dict( ( row[ 'Date' ],
                                 dict( ( ( ticker, row[ ticker ] ) 
                                         for ticker in tickerList ) ) )
                               for row in csvReader
                               if row[ 'Date' ] >= begin and row[ 'Date' ] <= end )
        
    return empiricalTable
    
if __name__ == "__main__":
    files = getDailyFileList( datetime.date( 2012, 1, 30 ),
                              mergeWeekendsWithMonday = True )
    for f in files:
        print f
