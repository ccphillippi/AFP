'''
Created on Jan 31, 2014

@author: Christopher Phillippi
'''

from itertools import chain
import afp

def formatAlias( alias ):
    return alias.lower()

def formatTicker( ticker ):
    return ticker.upper()

def formatName( name ):
    return name.title()
    
def getAliasToKeywordMap( filename ):
    def getAllKeywordPairs( f ):
        def aliasToKeywordPairs( row ):
            def getAliases( aliasArray ):
                return [ formatAlias( alias ) for alias in aliasArray if alias != "" ]
            aliases = getAliases( row.split( ',' ) )
            keyword = aliases[ 0 ]
            return ( ( alias, keyword ) for alias in aliases )
        return chain.from_iterable( ( aliasToKeywordPairs( row ) 
                                      for i, row in enumerate( f ) 
                                      if i != 0 ) )
    with open( filename, 'r' ) as f:
        return dict( getAllKeywordPairs( f ) )
    return dict()

def getKeywordToIndexMap( filename ):
    def aliasToIndexPairs( row ):
            def getAliases( aliasArray ):
                return [ formatAlias( alias ) for alias in aliasArray if alias != "" ]
            aliases = getAliases( row.split( ',' ) )
            keyword = aliases[ 0 ]
            return ( ( alias, keyword ) for alias in aliases )
    keywordsToFieldsMap = getKeywordToFieldsMap( filename )
    return dict( ( ( alias, i )
                   for fields in keywordsToFieldsMap 
                   for alias, i in aliasToIndexPairs( fields ) ) )

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
        return dict( getAllKeywordToFieldsPairs( f ) )
    return dict()
    
for alias, keyword in  getAliasToKeywordMap( afp.settings.KEYWORDS_FILEPATH ).iteritems():
    print "%s->%s" % ( alias, keyword )

for keyword, fields in getKeywordToFieldsMap( afp.settings.KEYWORDS_FILEPATH ).iteritems():
    print keyword, ": "
    for field, value in fields.iteritems():
        print "\t%6s: %s" % ( field, value )
