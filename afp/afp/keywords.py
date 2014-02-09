'''
.. module:: keywords

This module handles the keyword mappings required when counting words in articles for matrix generation

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

from itertools import chain
from string import capwords
import afp.settings as settings

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
    
    >>> formatName( r'someone\'s financial GROUP' )
    'Someone's Financial Group'
    
    """
    return capwords( name.title() )

def getKeywordToIndexMap( csvFile ):
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
    
def getIndexToFieldsMap( csvFile ):
    """Returns a dictionary with indices as keys and fields as values given keywords *csvFile* path
    
    :param csvFile: The path of the keywords *.csv* file
    """
    return dict( ( ( field[ "Index" ], field ) 
                   for field in getKeywordToFieldsMap( csvFile ).itervalues() ) )    
    
def getAliasToKeywordMap( csvFile ):
    """Returns a dictionary with aliases as keys and keywords as values given keywords *csvFile* path
    
    :param csvFile: The path of the keywords *.csv* file
    """
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
    with open( csvFile, 'r' ) as keywordsCsv:
        keywordPairs = getAllKeywordPairs( keywordsCsv.readlines() )
    return dict( keywordPairs )

def getKeywordToFieldsMap( csvFile ):
    """Returns a dictionary with keywords as keys and fields as values given keywords *csvFile* path
    
    :param csvFile: The path of the keywords *.csv* file
    """
    def getAllKeywordToFieldsPairs( f ):
        def getKeywordToFieldsPair( i, row ):
            columns = row.strip().split( ',' )
            fields = { "Index": i,
                       "Name" : formatName( columns[ 0 ] ),
                       "Ticker" : formatTicker( columns[ 1 ] ),
                       "Others" : [ formatAlias( column ) for column in columns[ 2: ] if column != "" ] }
            return ( formatAlias( columns[ 0 ] ), fields )
        return ( getKeywordToFieldsPair( i - 1, row ) for i, row, in enumerate( f ) if i != 0 ) 
    with open( csvFile, 'r' ) as f:
        pairs = getAllKeywordToFieldsPairs( f.readlines() )
    return dict( pairs )
    
# for alias, keyword in  getAliasToKeywordMap( settings.KEYWORDS_FILEPATH ).iteritems():
#    print "%s->%s" % ( alias, keyword )
if __name__ == "__main__":
    for key, value in getKeywordToIndexMap( settings.KEYWORDS_FILEPATH ).iteritems():
        print key, ": ", value
