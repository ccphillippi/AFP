'''
.. module:: strategies

This module contains the backtesting strategies

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import datetime
import normalize
import numpy as np
import numpy.linalg as nplinalg
import pandas as pd
import matplotlib.pyplot as plt

import matrices
import keywords
import count
import sentiment

class Backtest( object ):
    class Results( object ):
        _daysPerYear = 252
        def __init__( self,
                      returns, 
                      tradeDates,
                      name = 'Returns',
                      budget = 1,
                      stocks = None,
                      weights = None,
                      riskFree = 0.001, 
                      benchmarkPrices = None ):
            self.budget = budget
            self.weights = pd.DataFrame( np.hstack( weights ).T,
                                         index = tradeDates,
                                         columns = stocks )
            self.returns = pd.DataFrame( np.array( returns ),
                                         index = tradeDates,
                                         columns = [ name ] )
            try:
                self.begin = tradeDates[ 0 ].date()
            except AttributeError:
                self.begin = tradeDates[ 0 ]
            try:
                self.end = tradeDates[ -1 ].date()
            except AttributeError:
                self.end = tradeDates[ -1 ]
            self.riskFree = riskFree
            self.benchmarkPrices = benchmarkPrices
        def timeSpan( self, freq = 'years' ):
            if freq == 'days':
                return ( self.end - self.begin ).days
            if freq == 'years':
                return float( ( self.end - self.begin ).days ) / self._daysPerYear
        def cumulativeReturns( self ):
            return ( self.returns + 1 ).cumprod()
        def portfolioValues( self ):
            return self.cumulativeReturns() * self.budget
        def totalReturn( self ):
            return self.cumulativeReturns().as_matrix()[-1] - 1
        def annualizedReturn( self ):
            return self.totalReturn() / self.timeSpan()
        def annualizedRisk( self ):
            return float( np.std( self.returns.as_matrix() ) * np.sqrt( self._daysPerYear ) )
        def sharpeRatio( self ):
            return ( self.annualizedReturn() - self.riskFree ) / self.annualizedRisk()
        def informationRatio( self ):
            if self.benchmarkPrices == None:
                raise Exception( 'Benchmark not provided for Information Ratio.' )
            factorReturns = self.benchmarkPrices.pct_change().ix[ self.returns.index ]
            cov = np.cov( self.returns, factorReturns )
            var = np.var( self.returns )
            beta = cov / var
            benchmarkReturns = beta * factorReturns
            benchmarkReturn = Backtest.Results( benchmarkReturns, self.returns.index ).annualizedReturn()
            activeRisk = Backtest.Results( self.returns - benchmarkReturns, self.returns.index ).annualizedRisk()
            return ( self.annualizedReturn() - benchmarkReturn ) / activeRisk
            
            
            
    def __init__( self, 
                  prices,
                  counts,
                  strategy, 
                  budget = 1,
                  trainDays = 252,
                  rho = 1,
                  riskFree = 0.01,
                  benchmarkPrices = None ):
        self.dates = prices.index
        self.prices = prices
        self.counts = counts
        self.returns = prices.pct_change()
        self.vol = pd.ewmstd( self.returns, span = trainDays )
        self.price_corr = pd.expanding_corr_pairwise( self.returns, trainDays )
        self.strategy = strategy
        self.budget = budget
        self.trainDates = self.dates[1:( trainDays + 1 )]
        self.tradeDates = self.dates[( trainDays + 1 ):]
        self.rho = rho
        self.riskFree = riskFree
        self.benchmarkPrices = benchmarkPrices
    
    def run( self  ):
        yesterday = self.trainDates[ -1 ]
        ptfReturns = dict()
        weights = dict()
        for date in self.tradeDates:
            datetime = date.date()
            newsCorr = normalize.TfIdf()( self.counts.ix[ :yesterday.date() ] ).corr().to_dense()
            empCorr = self.price_corr[ yesterday.date() ]
            nans = newsCorr != newsCorr
            newsCorr[ nans ] = empCorr[ nans ]
            corr = ( 1 - self.rho ) * empCorr + self.rho * newsCorr
            vol = self.vol.ix[ yesterday ]
            cov = corr * np.outer( vol, vol )
            weights[ date ] = self.strategy.getWeights( cov.as_matrix() )
            ptfReturns[ date ] = float( np.dot( self.returns.ix[ datetime ], weights[ date ] ) )
            yesterday = date
        
        allWeights, returns = zip( *( ( weights[ date ], ptfReturns[ date ] ) 
                                      for date in self.tradeDates ) )
        return ( Backtest.Results( returns,
                                   self.tradeDates,
                                   name = self.strategy.getName(),
                                   budget = self.budget,
                                   weights = allWeights,
                                   stocks = self.counts.columns,
                                   riskFree = self.riskFree,
                                   benchmarkPrices = self.benchmarkPrices ) )

class RiskOnlyStrategy( object ):
    def getWeights( self, cov ):
        raise NotImplemented
    

class MinimumVariance( RiskOnlyStrategy ):
    def getName( self ):
        return 'Minimum Variance'
    def getWeights( self, cov ):
        ones = np.ones( ( cov.shape[ 0 ], 1 ) )
        invCovOnes = nplinalg.solve( cov, ones )
        return invCovOnes / ( np.dot( ones.T, invCovOnes ) )

if __name__ == '__main__':
    begin = datetime.date( 2011, 1, 3 )
    end = datetime.date( 2013, 11, 27 )
    tickerList = keywords.getTickerList()
    keywordsMap = keywords.getKeywordToIndexMap()
    empiricalDf = matrices.getEmpiricalDataFrame( tickerList, begin, end )
    countDf = matrices.getCountDataFrame( tickerList,
                                 count.SentimentWordCounter( keywordsMap,
                                                             sentiment.classifier() ),
                                 empiricalDf.index,
                                 aggregator = np.sum )
    backtest = Backtest( empiricalDf, countDf, MinimumVariance(), budget = 1, trainDays = 252, rho = 0.3 )
    results = backtest.run()
    results.cumulativeReturns().plot(); plt.legend( loc = 'best' ); plt.show()
    print results.sharpeRatio()
    print results.totalReturn()
