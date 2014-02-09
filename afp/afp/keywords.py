'''
Created on Jan 31, 2014

@author: Christopher Phillippi
'''

from itertools import chain
from string import capwords
import afp.settings as settings

def formatAlias( alias ):
    return alias.lower()

def formatTicker( ticker ):
    return ticker.upper()

def formatName( name ):
    return capwords( name.title() )

def getKeywordToIndexMap( filename ):
    fields = getKeywordToFieldsMap( filename ).itervalues()
    def aliasToIndexPairs():
        def getAliases( field ):
            keywords = [ field[ "Name" ], field[ "Ticker" ] ] + field[ "Others" ]
            return ( formatAlias( alias ) for alias in keywords if alias != "" )
        return ( ( alias, field[ "Index" ] ) 
                 for field in fields 
                 for alias in getAliases( field ) )
    return dict( aliasToIndexPairs() )
    
def getIndexToFieldsMap( filename ):
    return dict( ( ( field[ "Index" ], field ) 
                   for field in getKeywordToFieldsMap( filename ).itervalues() ) )    
    
def getAliasToKeywordMap( filename ):
    def getAllKeywordPairs( rows ):
        def aliasToKeywordPairs( row ):
            def getAliases( aliasArray ):
                return [ formatAlias( alias ) for alias in aliasArray if alias != "" ]
            aliases = getAliases( row.split( ',' ) )
            keyword = aliases[ 0 ]
            return ( ( alias, keyword ) for alias in aliases )
        return chain.from_iterable( ( aliasToKeywordPairs( row.strip() ) 
                                      for i, row in enumerate( rows ) 
                                      if i != 0 ) )
    with open( filename, 'r' ) as keywordsCsv:
        keywordPairs = getAllKeywordPairs( keywordsCsv.readlines() )
    return dict( keywordPairs )

def getKeywordToFieldsMap( filename ):
    def getAllKeywordToFieldsPairs( f ):
        def getKeywordToFieldsPair( i, row ):
            columns = row.strip().split( ',' )
            fields = { "Index": i,
                       "Name" : formatName( columns[ 0 ] ),
                       "Ticker" : formatTicker( columns[ 1 ] ),
                       "Others" : [ formatAlias( column ) for column in columns[ 2: ] if column != "" ] }
            return ( formatAlias( columns[ 0 ] ), fields )
        return ( getKeywordToFieldsPair( i - 1, row ) for i, row, in enumerate( f ) if i != 0 ) 
    with open( filename, 'r' ) as f:
        pairs = getAllKeywordToFieldsPairs( f.readlines() )
    return dict( pairs )
    
# for alias, keyword in  getAliasToKeywordMap( settings.KEYWORDS_FILEPATH ).iteritems():
#    print "%s->%s" % ( alias, keyword )
if __name__ == "__main__":
    for key, value in getKeywordToIndexMap( settings.KEYWORDS_FILEPATH ).iteritems():
        print key, ": ", value
