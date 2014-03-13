'''
Created on Mar 13, 2014

@author: curly
'''

import afp.keywords as keywords
import afp.matrices as matrices
import afp.settings as settings
import cleaner.retrieve as retrieve
import pandas as pd
import datetime
import os

if __name__ == '__main__':
    begin = datetime.date( 2011, 1, 3 )
    end = datetime.date( 2013, 11, 27 )
    tickerList = keywords.getTickerList( os.path.join( settings.KEYWORDS_DIR, 'splist.csv' ) )
    filepath = retrieve.adjustedClosesFilepath( filename = 'cleanSP.csv' )
    dailyPrices = matrices.getEmpiricalDataFrame( tickerList, begin, end, csvPath = filepath )
    normalizedPrices = dailyPrices / dailyPrices.ix[ 0 ]
    pairs = dict( ( first + '|' + second,
                    sum( ( normalizedPrices[ first ] - normalizedPrices[ second ] ) ** 2 ) )
                  for first in normalizedPrices.columns
                  for second in normalizedPrices.columns
                  if first < second )
    pairDf = pd.DataFrame( pairs, index = ['Pairs'] ).T
    pairDf.to_csv( os.path.join( settings.RESULTS_DIR, 'leastSqPairs.csv' ) )
