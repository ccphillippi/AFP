'''
.. module:: strategies

This module contains the backtesting strategies

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

from pandas.stats.api import ols

import datetime
import normalize
import numpy as np
import numpy.linalg as nplinalg
import pandas as pd
import os
import matplotlib.pyplot as plt
import scipy.optimize as optimize

import cleaner.retrieve as retrieve
import matrices
import keywords
import count
import sentiment
import settings

class Backtest( object ):
    class Results( object ):
        _daysPerYear = 252
        _tol = 0.000000000001
        def __init__( self,
                      returns, 
                      tradeDates,
                      rho = None,
                      name = 'Returns',
                      riskModelName = 'NA',
                      budget = 1,
                      stocks = None,
                      weights = None,
                      riskFree = 0.001, 
                      benchmarkPrices = None ):
            self.name = name
            self.riskModelName = riskModelName
            self.rho = rho
            self.budget = budget
            try:
                self.weights = pd.DataFrame( np.hstack( weights ).T,
                                             index = tradeDates,
                                             columns = stocks )
            except TypeError:
                pass
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
                return float( self.timeSpan( freq = 'days' ) ) / 365.0
        def cumulativeReturns( self ):
            return ( self.returns + 1 ).cumprod() - 1
        def portfolioValues( self ):
            return ( 1 + self.cumulativeReturns() ) * self.budget
        def totalReturn( self ):
            return float( self.cumulativeReturns().as_matrix()[-1] ) 
        def annualizedReturn( self ):
            return self.totalReturn() / self.timeSpan()
        def annualizedRisk( self ):
            return float( np.std( self.returns.as_matrix() ) * np.sqrt( self._daysPerYear ) )
        def sharpeRatio( self ):
            return ( self.annualizedReturn() - self.riskFree ) / self.annualizedRisk()
        def informationRatio( self ):
            if type( self.benchmarkPrices ) == type( None ):
                raise Exception( 'Benchmark not provided for Information Ratio.' )
            returns = self.returns[1:]  # ignore first day tcosts
            factorReturns = self.benchmarkPrices.pct_change().ix[ returns.index ]
            factors = factorReturns.columns
            beta = ols( y = returns[ self.name ], x = factorReturns ).beta[ factors ]
            benchmarkReturns = ( beta * factorReturns ).sum( axis = 1 )
            benchmarkTest = Backtest.Results( returns - benchmarkReturns, returns.index )
            activeReturn = benchmarkTest.annualizedReturn()
            activeRisk = benchmarkTest.annualizedRisk()
            if np.abs( activeReturn ) < self._tol:
                return 0
            return activeReturn / activeRisk
        def toDataFrame( self ):
            columns = [ 'Strategy',
                        'Risk Model',
                        'Rho',
                        'Budget',
                        'Begin',
                        'End',
                        'Days',
                        'Years',
                        'Total Return',
                        'Annualized Return',
                        'Annualized Risk',
                        'Sharpe Ratio' ]
            values = [  self.name,
                        self.riskModelName,
                        self.rho,
                        self.budget,
                        self.begin,
                        self.end,
                        self.timeSpan( 'days' ),
                        self.timeSpan( 'years' ),
                        self.totalReturn(),
                        self.annualizedReturn(),
                        self.annualizedRisk(),
                        self.sharpeRatio() ] 
            try:
                values.append( self.informationRatio() )
                columns.append( 'Information Ratio' )
            except:
                pass
            values = np.array( [values] )
            return pd.DataFrame( values, columns = columns )
            
    def __init__( self, 
                  prices,
                  riskModel,
                  strategy,
                  begin,
                  end,
                  budget = 1,
                  rho = 1,
                  riskFree = 0.01,
                  tCosts = 0.001 ):
        self.dates = prices.index
        self.prices = prices
        self.riskModel = riskModel
        self.returns = prices.pct_change()
        self.strategy = strategy
        self.budget = budget
        self.trainDates = self.prices.ix[:begin].index
        self.tradeDates = self.prices.ix[begin:end].index
        self.rho = rho
        self.riskFree = riskFree
        self.benchmarkPrices = self.strategy.getBenchmark()
        self.tCosts = tCosts
    def run( self  ):
        def delever( weights ):
            return weights / np.sum( np.abs( weights ) )
        yesterday = self.trainDates[ -1 ]
        ptfReturns = dict()
        weights = { yesterday : np.zeros( ( self.prices.shape[1], 1 ) ) }
        yesterdaysValue = self.budget
        for date in self.tradeDates:
            cov = self.riskModel.getCovariance( yesterday, rho = self.rho )
            weights[ date ] = delever( self.strategy.getWeights( cov ) )
            weightChange = weights[ date ] - weights[ yesterday ]
            transCharge = self.tCosts * yesterdaysValue * np.sum( abs( weightChange ) )
            returns = float( np.dot( self.returns.ix[ date.date() ], weights[ date ] ) )
            todaysValue = ( 1 + returns ) * yesterdaysValue - transCharge
            ptfReturns[ date ] = ( todaysValue - yesterdaysValue ) / yesterdaysValue
            yesterday = date
        
        allWeights, returns = zip( *( ( weights[ date ], ptfReturns[ date ] ) 
                                      for date in self.tradeDates ) )
        return ( Backtest.Results( returns,
                                   self.tradeDates,
                                   rho = self.rho,
                                   name = self.strategy.getName(),
                                   riskModelName = self.riskModel.getName(),
                                   budget = self.budget,
                                   weights = allWeights,
                                   stocks = self.prices.columns,
                                   riskFree = self.riskFree,
                                   benchmarkPrices = self.benchmarkPrices ) )

class RiskModel( object ):
    def dyad( self, x ):
        return np.outer( x, x )
    def getCovariance( self, date ):
        raise NotImplemented
    def getVolDyad( self, date ):
        raise NotImplemented
    def getName( self ):
        return self.name
    def getDates( self ):
        return self.dates
    
class EmpiricalCovariance( RiskModel ):
    def __init__( self, 
                  prices, 
                  volFunc = lambda returns: pd.ewmstd( returns, span = 252 ), 
                  name = 'Empirical'  ):
        self.name = name
        self.dates = prices.index
        self.returns = prices.pct_change()
        self.vol = volFunc( self.returns )
        self.volDyad = dict( ( today, self.dyad( self.vol.ix[ today.date() ] ) ) for today in self.dates )
        self.empCov = dict( ( today, self.returns[ 1:today.date() ].corr().as_matrix() * self.volDyad[ today ] )
                              for today in self.dates[1:] )
    def getCovariance( self, date, **kwargs ):
        return self.empCov[ date ]
    def getVolDyad( self, date ):
        return self.volDyad[ date ]

class ShrunkCovarianceModel( RiskModel ):
    def __init__( self, baseModel, name = 'Shrinkage (Constant Corr)' ):
        self.baseModel = baseModel
        self.name = name
        self.dates = baseModel.getDates()
    def getCovariance( self, date, rho ):
        cov = self.baseModel.getCovariance( date, rho = rho )
        constantCorr = rho*np.ones( cov.shape )
        np.fill_diagonal( constantCorr, 1 )
        vol = np.sqrt( np.diag( cov ) )
        shrinkCov = np.outer( vol, vol ) * constantCorr
        return ( 1 - rho ) * cov + shrinkCov
        
class NewsCovarianceModel( RiskModel ):
    def __init__( self, 
                  baseModel, 
                  counts,  
                  name = 'NewsCovariance' ):
        def tfIdfCov( today ):
            return normalize.TfIdf()( counts.ix[ :today.date() ] ).corr().as_matrix() * self.baseModel.getVolDyad( today )
        self.name = name
        counts = counts.to_dense()
        self.baseModel = baseModel
        self.dates = self.baseModel.getDates()
        self.newsCov = dict( ( today, tfIdfCov( today ) )
                             for today in self.dates[1:] )
        for date in self.dates[1:]:
            newsCov = self.newsCov[ date ]
            empCov = self.baseModel.getCovariance( date )
            nans = newsCov != newsCov
            self.newsCov[ date ][ nans ] = empCov[ nans ]
    def getCovariance( self, date, rho = 0 ):
        return rho * self.newsCov[ date ] + ( 1 - rho ) * self.baseModel.getCovariance( date )
    def getVolDyad( self, date ):
        return self.baseModel.getVolDyad( date )
    def getName( self ):
        return self.name
    def getDates( self ):
        return self.dates
        
class RiskOnlyStrategy( object ):
    _min = 0
    _max = None
    def getWeights( self, cov ):
        raise NotImplemented
    def getName( self ):
        return self.name
    def getBenchmark( self ):
        return self.benchmark

class MinimumVariance( RiskOnlyStrategy ):
    _constraints = ( {'type': 'eq', 'fun': lambda x: np.sum( x ) - 1 } )
    def __init__( self, benchmark = None, constrained = False ):
        self.name = 'Minimum Variance'
        self.benchmark = benchmark
        self.constrained = constrained
    def getWeights( self, cov ):
        def constrained():
            def obj( x ):
                return np.dot( x, np.dot( cov, x ) )
            n = float( cov.shape[ 0 ] )
            x0 = np.ones( ( n, 1 ) ) / n
            solution = optimize.minimize( obj, x0, method = 'SLSQP',
                                          bounds = tuple( ( self._min, self._max ) for _ in range( 0, int( n ) ) ),
                                          constraints = self._constraints )
            weights = solution.x
            weights.shape = ( n, 1 )
            return weights
        def analytical():
            ones = np.ones( ( cov.shape[ 0 ], 1 ) )
            invCovOnes = nplinalg.solve( cov, ones )
            return invCovOnes / np.sum( invCovOnes )
        if self.constrained:
            return constrained()
        return analytical()

class MaximumDiversification( RiskOnlyStrategy ):
    def __init__( self, benchmark = None, constrained = False ):
        self.name = 'Maximum Diversification'
        self.benchmark = benchmark
        self.constrained = constrained 
    def getWeights( self, cov ):
        vol = np.sqrt( np.diag( cov ) )
        def constrained():
            n = float( cov.shape[ 0 ] )
            constraints = ( {'type': 'eq', 'fun': lambda x: np.dot( x, vol ) - 1 } )
            bounds = tuple( ( self._min , self._max ) for _ in range( 0, int( n ) ) )
            def obj( x ):
                return np.dot( x, np.dot( cov, x ) )
            x0 = np.ones( ( n, 1 ) ) / n
            solution = optimize.minimize( obj, x0, method = 'SLSQP', bounds = bounds, constraints = constraints )
            weights = solution.x
            weights.shape = ( n, 1 )
            return weights / np.sum( weights )
        def analytical():
            invCovVol = nplinalg.solve( cov, vol )
            weights = invCovVol / np.sum( invCovVol )
            weights.shape = ( weights.shape[ 0 ], 1 )
            return weights
        if self.constrained:
            return constrained()
        return analytical()

class RiskParity( RiskOnlyStrategy ):
    _constraints = ( { 'type': 'eq', 'fun': lambda x: np.sum( x[:-1] ) - 1 } )
    _avgVol = 0.10 / 65.0
    def __init__( self, benchmark = None ):
        self.name = 'Risk Parity'
        self.benchmark = benchmark
    def getWeights( self, cov ):
        def obj( xi ):
            phi = xi[-1]
            x = xi[:-1]
            diff = x * np.dot( cov, x ) - phi
            return np.dot( diff, diff )
                
        n = float( cov.shape[ 0 ] )
        bounds = tuple( ( self._min , self._max ) for _ in range( 0, int( n ) + 1 ) )       
        x0 = np.concatenate( ( np.ones( ( n, 1 ) ), [[ self._avgVol ]] ) )
        solution = optimize.minimize( obj, x0, method = 'SLSQP', bounds = bounds, constraints = self._constraints )
        weights = solution.x[:-1]
        weights.shape = ( n, 1 )
        return weights

def testStrategies( empiricalDf, riskModels, strategies, dateRanges, rhos, budget = 1 ):
    def getPortfolio( result ):
        def valueWithStrategy( result ):
            values = result.portfolioValues()
            values.rename( columns = { result.name : 'Returns' }, inplace = True )
            values.insert( 0, 'Strategy', result.name )
            return values
        values = valueWithStrategy( result )
        df = pd.merge( values, result.toDataFrame(), on = 'Strategy' )
        df.index = values.index
        return df
    results = [ Backtest( empiricalDf,
                          riskModel,
                          strategy,
                          begin,
                          end,
                          budget = budget,
                          rho = rho ).run()
                   for strategy in strategies
                   for begin, end in dateRanges
                   for rho in rhos
                   for riskModel in riskModels ]
    portfolios = [ getPortfolio( result ) for result in results ] 
    return ( results, portfolios )
# if __name__ == '__main__':
#     begin = datetime.date( 2011, 1, 3 )
#     end = datetime.date( 2013, 11, 27 )
#     tickerList = keywords.getTickerList()
#     keywordsMap = keywords.getKeywordToIndexMap()
#     sentCounter = count.SentimentWordCounter( keywordsMap, sentiment.classifier() )
#     mentionCounter = count.WordCounter( keywordsMap )
#     empiricalDf = matrices.getEmpiricalDataFrame( tickerList, begin, end )
#     constrained = False
#     minVarBenchmark = { True : 'minvarConstrained.csv', False : 'minvarAnalytical.csv' }
#     maxDivBenchmark = { True : 'maxDivConstrained.csv', False : 'maxDivAnalytical.csv' }
#     minvarBenchmarkDf = matrices.getEmpiricalDataFrame( [ MinimumVariance().getName() ], begin, end, retrieve.adjustedClosesFilepath( filename = minVarBenchmark[ constrained ] ) )  
#     maxDivBenchmarkDf = matrices.getEmpiricalDataFrame( [ MaximumDiversification().getName() ], begin, end, retrieve.adjustedClosesFilepath( filename = maxDivBenchmark[ constrained ] ) )
#     riskParityDf = matrices.getEmpiricalDataFrame( [ RiskParity().getName() ], begin, end, retrieve.adjustedClosesFilepath( filename = 'riskParity.csv' ) )   
#     benchmarkDf = matrices.getEmpiricalDataFrame( [ 'OEF', 'SPY' ], begin, end, retrieve.benchmarkFilepath() )
#     summedSentDf = matrices.getCountDataFrame( tickerList, sentCounter, empiricalDf.index, aggregator = np.sum )
#     articleSentDf = matrices.getCountDataFrame( tickerList, sentCounter, empiricalDf.index )
#     summedMentionDf = matrices.getCountDataFrame( tickerList, mentionCounter, empiricalDf.index, aggregator = np.sum )
#     articleMentionDf = matrices.getCountDataFrame( tickerList, mentionCounter, empiricalDf.index )
#     empiricalDf = empiricalDf.ix[:, summedMentionDf.columns ]
#     empiricalCov = EmpiricalCovariance( empiricalDf )
#     
#     saveBenchmarks = False
#     if saveBenchmarks:
#         beginBench = begin + datetime.timedelta( 20 ) 
#         for constrained in [ True, False ]:
#             minvar = Backtest( empiricalDf, empiricalCov, MinimumVariance( constrained = constrained ), beginBench, end ).run().portfolioValues()
#             minvar.to_csv( os.path.join( settings.RESULTS_DIR, minVarBenchmark[ constrained ] ) )
#             maxdiv = Backtest( empiricalDf, empiricalCov, MaximumDiversification( constrained = constrained ), beginBench, end ).run().portfolioValues()
#             maxdiv.to_csv( os.path.join( settings.RESULTS_DIR, maxDivBenchmark[ constrained ] ) )
#         riskpar = Backtest( empiricalDf, empiricalCov, RiskParity(), beginBench, end ).run().portfolioValues()
#         riskpar.to_csv( os.path.join( settings.RESULTS_DIR, 'riskParity.csv' ) )
#         print 'Benchmarks Cached'    
#     
#     riskModels = [ 
#                    NewsCovarianceModel( empiricalCov, summedSentDf, name = 'Daily Summed Sentiment' ),
#                    NewsCovarianceModel( empiricalCov, articleSentDf, name = 'Article Sentiment' ),
#                    NewsCovarianceModel( empiricalCov, summedMentionDf, name = 'Daily Summed Mention' ),
#                    NewsCovarianceModel( empiricalCov, articleMentionDf, name = 'Article Mention' ),
#                    ShrunkCovarianceModel( empiricalCov )
#                  ]
#                    
#     strategies = [ MinimumVariance( benchmark = minvarBenchmarkDf, constrained = constrained ),
#                    MaximumDiversification( benchmark = maxDivBenchmarkDf, constrained = constrained ),
#                    RiskParity( benchmark = riskParityDf ) 
#                  ]
#     rhos = np.linspace( 0, 1, 21 )
#     beginDates = [ datetime.date( 2011, 11, 5 ), datetime.date( 2012, 11, 6 ) ]
#     endDates = [ beginDates[ 1 ] - datetime.timedelta( 1 ), end ]
#     
#     allResults, portfolios = testStrategies( empiricalDf, riskModels, strategies, zip( beginDates, endDates ), rhos )
#     resultsDf = pd.concat( ( result.toDataFrame() for result in allResults ) )
#     portfoliosDf = pd.concat( portfolios )
#     print resultsDf
#     resultsDf.to_csv( os.path.join( settings.RESULTS_DIR , 'strategiesResults_conservative.csv' ) )
#     portfoliosDf.to_csv( os.path.join( settings.RESULTS_DIR , 'strategiesPortfolios_conservative.csv' ) )
