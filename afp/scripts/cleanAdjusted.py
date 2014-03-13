'''
Created on Mar 12, 2014

@author: curly
'''

import datetime
import afp.matrices as matrices
import afp.keywords as keywords
import afp.settings as settings
import cleaner.retrieve as retrieve
import os

if __name__ == '__main__':
    begin = datetime.date( 2011, 1, 3 )
    end = datetime.date( 2013, 11, 27 )
    tickerList = keywords.getTickerList( os.path.join( settings.KEYWORDS_DIR, 'splist.csv' ) )
    filepath = retrieve.adjustedClosesFilepath( filename = 'hftDaily.csv' )
    dailyPrices = matrices.getEmpiricalDataFrame( tickerList, begin, end, csvPath = filepath )
    n = dailyPrices.shape[ 0 ] 
    threshold = .01
    removedCols = dailyPrices.ix[ :, ( dailyPrices != dailyPrices ).sum() < threshold * n ]
    removedCols.to_csv( os.path.join( os.path.join( settings.RESULTS_DIR, 'cleanSP.csv' ) ) )

    
