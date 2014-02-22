'''
.. module:: store

High level API that stores uncleaned data into cleaned store

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import cleaner.helpers as helpers
import cleaner.settings as settings
import cleaner.filers as filers
import cleaner.schema as schema
import csv
import multiprocessing as mp
import os
import ystockquote

def cleanSources( uncleanStore, numWorkers = settings.MAX_WORKERS ):
    """Cleans all files in unclean directory, using numWorkers processors.
    
    :param numWorkers: Number of processors to allocate. Defaults to :py:func:`multiprocessing.cpu_count`
    
    Call this function directly to clean data. For example:
    
    >>> cleanSources( settings.UNCLEAN_STORE )
    Cleaning data in <C:\AFPunclean> with <8> workers.
    
    """
    pool = mp.Pool( numWorkers )
    print "Cleaning data in <%s> with <%d> workers." % ( uncleanStore, numWorkers )
    
    def clean( source ):
        try:
            filer = filers.BatchFiler( schema.getSchema( source ) )
        except Exception as e:
            return [e]
        sourceDir = os.path.join( settings.UNCLEAN_STORE, source )
        uncleaned = ( ( filer, sourceDir, uncleaned ) for uncleaned in os.listdir( sourceDir ) )
        return pool.map( _cleanFile, uncleaned )
    results = helpers.flatten( [ clean( source ) for source in os.listdir( uncleanStore ) ] )
    added = [ result for result in results if result.added  ]
    notAdded = [ result for result in results if not result.added ]
    return { "Added" : added, "Unable To Add" : notAdded }

def storeAdjustedClose( tickerList, fromDate, toDate, empiricalStore = 'C:\AFPempiricalstore', filename = 'adjustedClose.csv' ):
    """Stores a *.csv* file of the adjusted closes of the ticker list by ordered date in *empiricalStore*
    
    :param tickerList: List of tickers to be stored in csv from left to right
    :param fromDate: Start date to get historical closes from
    :type fromDate: :py:class:`datetime.date`
    :param toDate: End date to get historical closes from
    :type toDate: :py:class:`datetime.date`
    :param empiricalStore: The folder to store the *.csv* file
    :param filename: The file name of the .csv file
    
    For example:
    
    >>> storeAdjustedClose( [ 'GOOG', 'AAPL' ], datetime.date( 2012, 1, 10 ), datetime.date( 2012, 1, 30 ) )
    {'GOOG': {'2012-01-13': '624.99', '2012-01-12': '629.64', '2012-01-11': '625.96', ...
    
    """
    def getPath():
        path = os.path.abspath( empiricalStore )
        helpers.ensurePath( path )
        return os.path.join( path, filename )
    def adjustedCloseFor( ticker ):
        csvFile = ystockquote.get_historical_prices( ticker, str( fromDate ), str( toDate ) )
        return dict( ( ( date, row[ 'Adj Close' ] ) 
                       for i, ( date, row ) in enumerate( csvFile.iteritems() )
                       if i != 0 ) )
    adjustedCloses = [ adjustedCloseFor( ticker )  for ticker in tickerList ]
    minDate = max( [ min( adjClose.keys() ) for adjClose in adjustedCloses ] )
    maxDate = min( [ max( adjClose.keys() ) for adjClose in adjustedCloses ] )
    dates = [ date for date in sorted( adjustedCloses[ 0 ].keys() ) 
              if date >= minDate and date <= maxDate ]
    adjCloseByDate = dict( ( ( date, [ adjustedCloses[ i ][ date ] 
                                      for i in range( len( tickerList ) ) ] ) 
                             for date in dates ) )
    
    with open( getPath(), 'wb' ) as csvFile:
        csvWriter = csv.writer( csvFile )
        header = [ 'Date' ] + tickerList;
        csvWriter.writerow( header )
        for date, closes in sorted( adjCloseByDate.iteritems() ):
            csvWriter.writerow( [ date ] + closes )
    
    return dict( zip( tickerList, adjustedCloses ) )
# Multithreading library requires this be a function rather than method or inner function
# Unpickleable otherwise
def _cleanFile( args ):
    filer, cleanDir, uncleanFile = args
    return filer.write( os.path.join( cleanDir, uncleanFile ) )

if __name__ == '__main__':
    cleanSources( settings.UNCLEAN_STORE )
    
