'''
Created on Mar 13, 2014

@author: curly
'''

import afp.keywords as keywords
import afp.count as count
import afp.matrices as matrices
import afp.sentiment as sentiment
import afp.settings as settings
import afp.strategies as strats
import cleaner.retrieve as retrieve
import numpy as np
import pandas as pd
import datetime
import os

if __name__ == '__main__':
    begin = datetime.date( 2011, 1, 3 )
    end = datetime.date( 2013, 11, 27 )
    tickerList = keywords.getTickerList()
    keywordsMap = keywords.getKeywordToIndexMap()
    sentCounter = count.SentimentWordCounter( keywordsMap, sentiment.classifier() )
    mentionCounter = count.WordCounter( keywordsMap )
    empiricalDf = matrices.getEmpiricalDataFrame( tickerList, begin, end )
    constrained = False
    minVarBenchmark = { True : 'minvarConstrained.csv', False : 'minvarAnalytical.csv' }
    maxDivBenchmark = { True : 'maxDivConstrained.csv', False : 'maxDivAnalytical.csv' }
    minvarBenchmarkDf = matrices.getEmpiricalDataFrame( [ strats.MinimumVariance().getName() ], begin, end, retrieve.adjustedClosesFilepath( filename = minVarBenchmark[ constrained ] ) )  
    maxDivBenchmarkDf = matrices.getEmpiricalDataFrame( [ strats.MaximumDiversification().getName() ], begin, end, retrieve.adjustedClosesFilepath( filename = maxDivBenchmark[ constrained ] ) )
    riskParityDf = matrices.getEmpiricalDataFrame( [ strats.RiskParity().getName() ], begin, end, retrieve.adjustedClosesFilepath( filename = 'riskParity.csv' ) )   
    benchmarkDf = matrices.getEmpiricalDataFrame( [ 'OEF', 'SPY' ], begin, end, retrieve.benchmarkFilepath() )
    summedSentDf = matrices.getCountDataFrame( tickerList, sentCounter, empiricalDf.index, aggregator = np.sum )
    articleSentDf = matrices.getCountDataFrame( tickerList, sentCounter, empiricalDf.index )
    summedMentionDf = matrices.getCountDataFrame( tickerList, mentionCounter, empiricalDf.index, aggregator = np.sum )
    articleMentionDf = matrices.getCountDataFrame( tickerList, mentionCounter, empiricalDf.index )
    empiricalDf = empiricalDf.ix[:, summedMentionDf.columns ]
    empiricalCov = strats.EmpiricalCovariance( empiricalDf )
    
    saveBenchmarks = False
    if saveBenchmarks:
        beginBench = begin + datetime.timedelta( 20 ) 
        for constrained in [ True, False ]:
            minvar = strats.Backtest( empiricalDf, empiricalCov, strats.MinimumVariance( constrained = constrained ), beginBench, end ).run().portfolioValues()
            minvar.to_csv( os.path.join( settings.RESULTS_DIR, minVarBenchmark[ constrained ] ) )
            maxdiv = strats.Backtest( empiricalDf, empiricalCov, strats.MaximumDiversification( constrained = constrained ), beginBench, end ).run().portfolioValues()
            maxdiv.to_csv( os.path.join( settings.RESULTS_DIR, maxDivBenchmark[ constrained ] ) )
        riskpar = strats.Backtest( empiricalDf, empiricalCov, strats.RiskParity(), beginBench, end ).run().portfolioValues()
        riskpar.to_csv( os.path.join( settings.RESULTS_DIR, 'riskParity.csv' ) )
        print 'Benchmarks Cached'    
    
    riskModels = [ 
                   strats.NewsCovarianceModel( empiricalCov, summedSentDf, name = 'Daily Summed Sentiment' ),
                   strats.NewsCovarianceModel( empiricalCov, articleSentDf, name = 'Article Sentiment' ),
                   strats.NewsCovarianceModel( empiricalCov, summedMentionDf, name = 'Daily Summed Mention' ),
                   strats.NewsCovarianceModel( empiricalCov, articleMentionDf, name = 'Article Mention' ),
                   strats.ShrunkCovarianceModel( empiricalCov )
                 ]
                   
    strategies = [ strats.MinimumVariance( benchmark = minvarBenchmarkDf, constrained = constrained ),
                   strats.MaximumDiversification( benchmark = maxDivBenchmarkDf, constrained = constrained ),
                   strats.RiskParity( benchmark = riskParityDf ) 
                 ]
    rhos = np.linspace( 0, 1, 21 )
    beginDates = [ datetime.date( 2011, 11, 5 ), datetime.date( 2012, 11, 6 ) ]
    endDates = [ beginDates[ 1 ] - datetime.timedelta( 1 ), end ]
    
    allResults, portfolios = strats.testStrategies( empiricalDf, riskModels, strategies, zip( beginDates, endDates ), rhos )
    resultsDf = pd.concat( ( result.toDataFrame() for result in allResults ) )
    portfoliosDf = pd.concat( portfolios )
    print resultsDf
    resultsDf.to_csv( os.path.join( settings.RESULTS_DIR , 'strategiesResults_conservative.csv' ) )
    portfoliosDf.to_csv( os.path.join( settings.RESULTS_DIR , 'strategiesPortfolios_conservative.csv' ) )
