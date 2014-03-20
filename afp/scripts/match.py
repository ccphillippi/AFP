'''
Created on Mar 16, 2014

@author: curly
'''
import csv
import pandas
import os

class PairRetreiver(object):
    def __init__(self, dataDirectory ):
        self.directory = dataDirectory
    
    def get_data( self, com1, com2 ):
        octday = [ 1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 28, 29, 30, 31 ]
        d = pandas.DataFrame( columns = [ 'Times', 'Divergence', com1, com2, 'End_Of_Day', 'Threshold' ] )
        for i in octday:
            print "Processing 2012-10-" + format( i, '02d' )
            d = d.append( self.get_divergence( '2012-10-' + format( i, '02d' ), com1, com2 ) )
        return d
        
    
    def get_divergence( self, d, com1, com2 ):
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
            return pandas.DataFrame( columns = [ 'Times', 'Divergence', com1, com2, 'End_Of_Day', 'Threshold'] )
        
        dict1,dict2,div={},{},[]
        
        #Get Price for every Second
        for i in range(1,len(x1)):
            dict1[cal_second( x1[i][1].split( ' ' )[1].split( '.' )[0] )] = x1[i][7]
        for i in range(1,len(x2)):
            dict2[cal_second( x2[i][1].split( ' ' )[1].split( '.' )[0] )] = x2[i][7]
    
        #Find Opening Price
        i = 0
        while not( i in dict1 ):
            i += 1
        temp1 = dict1[i];
        i = 0
        while not( i in dict2 ):
            i += 1
        temp2=dict2[i];
    
        date = x1[1][1].split( " " )[0]
        P1, P2 = temp1, temp2
        threshold = 0.0005
        end=0
        for i in range(0,25201):
            if i == 25200: 
                end = 1
            if ( i in dict1 ) and ( i in dict2 ):
                temp1 = dict1[i]
                temp2 = dict2[i]
            elif ( i in dict1 ) and not ( i in dict2 ):
                temp1 = dict1[i]
            elif not ( i in dict1 ) and ( i in dict2 ):
                temp2 = dict2[i]
            div.append( [cal_stamp( date, i ), float( temp1 ) / float( P1 ) - float( temp2 ) / float( P2 ), float( temp1 ), float( temp2 ), end, threshold] )
        return pandas.DataFrame( div, columns = [ 'Times', 'Divergence', com1, com2, 'End_Of_Day', 'Threshold' ] )
            
