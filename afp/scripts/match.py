'''
Created on Mar 16, 2014

@author: curly
'''
import csv
from datetime import datetime
from datetime import timedelta
import pandas
import statsmodels.api as sm
import math
import numpy
import os
import ystockquote

class PairRetreiver(object):
    def __init__(self, dataDirectory ):
        self.directory = dataDirectory
    
    def _getHalfLife( self, prices, threshold = .5 ):
        """Fits an AR(1) model for the residuals to get the half life
            y_1 - y_2 = u
            u_t = C + \phi u_{t-1} + \epsilon
        
        Parameters
        ----------
        :param prices: price data frame (time x stocks)
        :param threshold: for the half life calculation, default to 0.1
        
        Call this function directly to calculate the half life for each stock in the price data frame
        """
        
        normalizedPrices = prices  # / prices.ix[ 0 ]
        
        hl_df = pandas.DataFrame()
        for first in normalizedPrices.columns:
            for second in normalizedPrices.columns:
                if first < second:
                    diff = normalizedPrices[ first ] - normalizedPrices[ second ]
                    phi = numpy.linalg.lstsq( numpy.array( [diff[:-1], numpy.ones( len( diff.shift() ) - 1 )] ).T, diff[1:] )[0][0]
                    hl_df[first + '|' + second] = [math.log( threshold ) / math.log( phi )]
        return hl_df.T
    def getPeriodsToExit( self, divergence, threshold = 0.5 ):
        ar_model = sm.tsa.AR( divergence )
        fit = ar_model.fit( maxlag = 1, method = 'mle' )
        phi = fit.params[1]
        print 'Periods to exit:', math.log( threshold ) / math.log( phi )
        return math.log( threshold ) / math.log( phi )
    def get_vol( self, com1, com2, date1, date2 ):
        d1 = datetime.strptime( date1, '%y-%m-%d' )
        d2 = datetime.strptime( date2, '%y-%m-%d' )
        p1 = ystockquote.get_historical_prices( com1, '20' + date1, '20' + date2 )
        p2 = ystockquote.get_historical_prices( com2, '20' + date1, '20' + date2 )
        dif = []
        for i in range( 0, ( d2 - d1 ).days + 1 ):
            if ( '20' + ( d1 + timedelta( days = i ) ).strftime( '%y-%m-%d' ) ) in p1:
                dif.append( float( p1['20' + ( d1 + timedelta( days = i ) ).strftime( '%y-%m-%d' )]['Close'] ) / float( p1['20' + date1]['Close'] ) - float( p2['20' + ( d1 + timedelta( days = i ) ).strftime( '%y-%m-%d' )]['Close'] ) / float( p2['20' + date1]['Close'] ) )
        return numpy.std( dif, axis = 0 )  
    
    def get_data( self, com1, com2 ):
        octday = [1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 28, 29, 30, 31]
        d = pandas.DataFrame( columns = ['Times', 'Divergence', com1, com2, 'End_Of_Day', 'Threshold'] )
        print "Calculating Threshold ..."
        threshold = self.get_vol( com1, com2, '10-01-04', '12-12-31' ) / math.sqrt( 252 * 6.5 * 60 * 60 ) * 2
        print "The threshold would be " + str( threshold )
        
        for i in octday:
            print "Processing 2012-10-" + format( i, '02d' )
            d = d.append( self.get_divergence( '2012-10-' + format( i, '02d' ), com1, com2, threshold ) )
        return d
    
    def get_theta( self, x ):
        l = len( x )
        logx = [math.log( i ) for i in x]
        dx = [a - b for a, b in zip( logx[:l - 1], logx[1 - l:] )]
        l = len( dx )
        r = numpy.corrcoef( dx[:l - 1], dx[1 - l:] )[0][1]
        theta = -1 / ( 2 * r ) * ( 1 - math.sqrt( 1 - 4 * r * r ) )
        return max( 0, theta )
        
    def get_divergence( self, d, com1, com2, threshold ):
        #file1='/Users/Lee/Documents/workspace/HFTProject/'+com1+d+'.csv'
        #file2='/Users/Lee/Documents/workspace/HFTProject/'+com2+d+'.csv'
        file1 = os.path.join( self.directory, com1 + d + '.csv' )
        file2 = os.path.join( self.directory, com2 + d + '.csv' )
        
        x1=[]
        x2=[]
        def cal_second( timestamp ):
            time = timestamp.split( ':' )
            sec = ( int( time[0] ) - 9 ) * 60 * 60 + ( int( time[1] ) ) * 60 + ( int( time[2] ) ) - 1800
            return sec
    
        def cal_stamp(date,i):
            i = i + 9 * 3600 + 30 * 60
            hour, minutes = divmod( i, 3600 )
            minutes, sec = divmod( minutes, 60 )
            return date + " " + format( hour, '02d' ) + ":" + format( minutes, '02d' ) + ":" + format( sec, '02d' )
    
        
        with open( file1, 'rU' ) as csvfile:
            reader = csv.reader( csvfile, delimiter = ',' )
            for row in reader:
                x1.append( row )
        with open( file2, 'rU' ) as csvfile:
            reader = csv.reader( csvfile, delimiter = ',' )
            for row in reader:
                x2.append( row )
        
        if len( x1 ) < 10 or len( x2 ) < 10:
            print "empty"
            return pandas.DataFrame( columns = ['Times', 'Divergence', com1, com2, 'End_Of_Day', 'Threshold'] )
        
        dict1,dict2,div={},{},[]
        
        P1, P2 = [], []
        #Get Price for every Second
        for i in range(1,len(x1)):
            dict1[cal_second( x1[i][1].split( ' ' )[1].split( '.' )[0] )] = x1[i][7]
            P1.append( float( x1[i][7] ) )
        for i in range(1,len(x2)):
            dict2[cal_second( x2[i][1].split( ' ' )[1].split( '.' )[0] )] = x2[i][7]
            P2.append( float( x2[i][7] ) )
    
        #Find Opening Price
        i = 0
        while not( i in dict1 ):
            i += 1
        temp1 = float( dict1[i] );
        i = 0
        while not( i in dict2 ):
            i += 1
        temp2 = float( dict2[i] );
    
        theta1 = self.get_theta( P1 );
        theta2 = self.get_theta( P2 );
    
        date = x1[1][1].split( " " )[0]
        P1, P2 = temp1, temp2
        EWM1, EWM2 = P1, P2
    
    
        end=0
        for i in range(0,25201):
            if i == 25200: end = 1
            if ( i in dict1 ) and ( i in dict2 ):
                temp1 = dict1[i]
                temp2 = dict2[i]
            elif ( i in dict1 ) and not ( i in dict2 ):
                temp1 = dict1[i]
            elif not ( i in dict1 ) and ( i in dict2 ):
                temp2 = dict2[i]
            EWM1 = theta1 * EWM1 + ( 1.0 - theta1 ) * float( temp1 )
            EWM2 = theta2 * EWM2 + ( 1.0 - theta2 ) * float( temp2 )
            div.append( [cal_stamp( date, i ), float( EWM1 ) / float( P1 ) - float( EWM2 ) / float( P2 ), float( temp1 ), float( temp2 ), end, threshold] )
        return pandas.DataFrame( div, columns = ['Times', 'Divergence', com1, com2, 'End_Of_Day', 'Threshold'] )
            
