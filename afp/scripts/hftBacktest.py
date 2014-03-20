'''
Created on Mar 16, 2014

@author: curly
'''
from match import PairRetreiver
import afp.settings as settings
import afp.strategies as strats
import itertools
import pandas as pd
import os

def testStrategies( allPairs ):
    def getPairType( x ): return x[ 0 ]
    def loadBacktest( tickerA, tickerB ):
        print 'Loading backtest for pair:', tickerA, '|', tickerB
        dataDirectory = os.path.join( os.path.expanduser( '~' ), 'Dropbox/MFE-Spring 2014/230X - HFT/Project/Data/Data' )
        retriever = PairRetreiver( dataDirectory )
        df = retriever.get_data( tickerA, tickerB )
        df.index = pd.to_datetime( df.ix[ :, 'Times'] )
        prices = df.ix[ :, [ tickerA, tickerB ] ]
        divergence = df.ix[ :, [ 'Divergence' ] ]
        threshold = df.ix[ :, [ 'Threshold' ] ]
        endOfDay = df.ix[ :, [ 'End_Of_Day' ] ]
        backtest = strats.PairsBacktest( prices,
                                     divergence,
                                     threshold,
                                     endOfDay,
                                     periodsToExit = 10000,
                                     budget = 1,
                                     riskFree = 0,
                                     tCosts = 0.000 ).run()
        backtest.portfolioValues().to_csv( os.path.join( settings.RESULTS_DIR, 'HFT/%s.csv' % ( tickerA + '_' + tickerB ) ) )
        return backtest
    def getStatsAndPortfolio( pairType, results ):
        numPairs = len( results )
        def valueWithStrategy():
            allValues = pd.DataFrame()
            sumReturns = pd.DataFrame()
            for result in results:
                pairReturns = result.returns.rename( columns = { result.name : 'Returns' },
                                                     inplace = False )
                sumReturns = sumReturns.add( pairReturns, fill_value = 0 )
                pairValues = result.portfolioValues().rename( columns = { result.name : 'Returns' },
                                                              inplace = False )
                pairValues[ 'PairType' ] = pairType
                pairValues[ 'Pair' ] = result.name
                allValues = allValues.append( pairValues )
            pairSetReturns = sumReturns / float( numPairs )
            fullBackTest = strats.Backtest.Results( pairSetReturns, 
                                                    pairSetReturns.index )
            resultsDf = fullBackTest.toDataFrame()
            resultsDf[ 'PairType' ] = pairType
            values = fullBackTest.portfolioValues()
            values[ 'PairType' ] = pairType
            values[ 'Pair' ] = 'aggregate'
            return ( resultsDf, allValues.append( values ) )
        return valueWithStrategy()
    results = [ ( pairType, loadBacktest( tickerA, tickerB ) )
                for pairType, pairs in allPairs.iteritems()
                for tickerA, tickerB in pairs ]
    stats, values = zip( *[ getStatsAndPortfolio( typeOfPair, [ result for _, result in pairs ] ) 
                            for typeOfPair, pairs in itertools.groupby( sorted( results,
                                                                                key = getPairType ),
                                                                       getPairType ) ] ) 
    
    return ( pd.concat( stats, axis = 0 ), pd.concat( values, axis = 0 ) )

lsPairs = [ [ 'ACE', 'CB'  ],
            [ 'PNW', 'WEC' ],
            [ 'TEG', 'XEL' ],
            [ 'ED' , 'SO'  ],
            [ 'SCG', 'XEL' ] ] 

newsPairs = [ [ 'AAPL', 'MSFT'  ],
              [ 'AAPL', 'GOOG'  ],
              [ 'T'   , 'VZ'    ],
              # [ 'UPS' , 'FEDEX' ],
              [ 'MSFT', 'GOOG'  ],
              [ 'PEP' , 'KO'    ] ]

precisionPairs = [ [ 'KMB' , 'WEC'  ],
                   [ 'ADP' , 'CINF' ],
                   [ 'CINF', 'CMS'  ],
                   [ 'KMB' , 'NI'   ],
                   [ 'ADP' , 'BTU'  ] ]

pairs = { 'Least Squares' : lsPairs, 'News' : newsPairs, 'Precision' : precisionPairs }
stats, values = testStrategies( pairs )
stats.to_csv( os.path.join( settings.RESULTS_DIR, 'HFT/stats.csv' ) )
values.to_csv( os.path.join( settings.RESULTS_DIR, 'HFT/values.csv' ) )
