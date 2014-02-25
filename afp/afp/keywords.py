'''
.. module:: keywords

This module handles the keyword mappings required when counting words in articles for matrix generation

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

from itertools import chain
from string import capwords
import afp.settings as settings
import csv

def formatAlias( alias ):
    """Formats a string in *Alias* format
    
    >>> formatAlias( 'A Particular Company' )
    'a particular company'
    
    """
    return alias.lower()

def formatTicker( ticker ):
    """Formats a string in *Ticker* format
    
    >>> formatTicker( 'boog' )
    'BOOG'
    
    """
    return ticker.upper()

def formatName( name ):
    """Formats a string in *Name* format
    
    >>> formatName( r"someone's financial GROUP" )
    'Someone's Financial Group'
    
    """
    return capwords( name.title() )

def getKeywordToIndexMap( csvFile = settings.KEYWORDS_FILEPATH ):
    """Returns a dictionary with keywords as keys and indices at values given keywords *csvFile* path
    
    :param csvFile: The path of the keywords *.csv* file
    """
    fields = getKeywordToFieldsMap( csvFile ).itervalues()
    def aliasToIndexPairs():
        def getAliases( field ):
            keywords = [ field[ "Name" ], field[ "Ticker" ] ] + field[ "Others" ]
            return ( formatAlias( alias ) for alias in keywords if alias != "" )
        return ( ( alias, field[ "Index" ] ) 
                 for field in fields 
                 for alias in getAliases( field ) )
    return dict( aliasToIndexPairs() )
    
def getIndexToFieldsMap( csvFile = settings.KEYWORDS_FILEPATH ):
    """Returns a dictionary with indices as keys and fields as values given keywords *csvFile* path
    
    :param csvFile: The path of the keywords *.csv* file
    """
    return dict( ( ( field[ "Index" ], field ) 
                   for field in getKeywordToFieldsMap( csvFile ).itervalues() ) )    
    
def getAliasToKeywordMap( csvFile = settings.KEYWORDS_FILEPATH ):
    """Returns a dictionary with aliases as keys and keywords as values given keywords *csvFile* path
    
    :param csvFile: The path of the keywords *.csv* file
    """
    def getAllKeywordPairs( rows ):
        def aliasToKeywordPairs( row ):
            def getAliases( aliasArray ):
                return [ formatAlias( alias ) for alias in aliasArray if alias != "" ]
            aliases = getAliases( row )
            keyword = aliases[ 0 ]
            return ( ( alias, keyword ) for alias in aliases )
        return chain.from_iterable( ( aliasToKeywordPairs( row ) 
                                      for i, row in enumerate( rows ) 
                                      if i != 0 ) )
    with open( csvFile, 'rU' ) as keywordsCsv:
        csvReader = csv.reader( keywordsCsv, dialect = 'excel' )
        keywordPairs = dict( getAllKeywordPairs( csvReader ) )
    return keywordPairs

def getKeywordToFieldsMap( csvFile = settings.KEYWORDS_FILEPATH ):
    """Returns a dictionary with keywords as keys and fields as values given keywords *csvFile* path
    
    :param csvFile: The path of the keywords *.csv* file
    """
    def getAllKeywordToFieldsPairs( f ):
        def getKeywordToFieldsPair( i, row ):
            fields = { "Index": i,
                       "Name" : formatName( row[ 0 ] ),
                       "Ticker" : formatTicker( row[ 1 ] ),
                       "Others" : [ formatAlias( column ) for column in row[ 2: ] if column != "" ] }
            return ( formatAlias( row[ 0 ] ), fields )
        return ( getKeywordToFieldsPair( i - 1, row ) for i, row, in enumerate( f ) if i != 0 ) 
    with open( csvFile, 'rU' ) as f:
        csvReader = csv.reader( f, dialect = 'excel' )
        keywordMap = dict( getAllKeywordToFieldsPairs( csvReader ) )
    return keywordMap

def getTickerList( csvFile = settings.KEYWORDS_FILEPATH ):
    indexToFieldMap = getIndexToFieldsMap( csvFile )
    return [ indexToFieldMap[ index ][ 'Ticker' ] for index in sorted( indexToFieldMap.keys() ) ]
    
    
# for alias, keyword in  getAliasToKeywordMap( settings.KEYWORDS_FILEPATH ).iteritems():
#    print "%s->%s" % ( alias, keyword )
if __name__ == "__main__":
    for value in getTickerList( settings.KEYWORDS_FILEPATH ):
        print value
