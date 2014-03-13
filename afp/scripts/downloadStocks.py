''''
.. module:: downloadStocks

An example of retrieving empirical equities data using cleaner

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import afp.keywords as keywords
import afp.settings as settings
import cleaner.store as store
import datetime
import os

if __name__ == '__main__':
    tickerList = keywords.getTickerList( os.path.join( settings.KEYWORDS_DIR, 'splist.csv' ) )
    fromDate = datetime.date( 2011, 1, 3 )
    toDate = datetime.date( 2013, 11, 27 )    
    store.adjustedClose( tickerList, fromDate, toDate, filename = 'spDaily.csv' )
