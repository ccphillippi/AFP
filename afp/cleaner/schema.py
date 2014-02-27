'''
.. module:: schema

Stores schema configurations, both for unclean and clean schemas

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import cleaner.filers as filers
import cleaner.settings as settings

#======================================
# Clean Schema
#======================================
def getFilePath( source, paper, month, day, year ):
    """Configures cleaned file system schema
    """
    attributes = { settings.SOURCE : source,
                   settings.PAPER  :  paper,
                   settings.MONTH  :  month,
                   settings.DAY    :    day,
                   settings.YEAR   :   year 
                 }
    return "\\".join( [ settings.CLEAN_STORE ] + [ attributes[ key ] 
                                                   for key in settings.STORE_ORDER ] )


#======================================
# Dirty Schemas
#======================================
def getSchema( sourceDirectory ):
    """Given a sourceDirectory, returns the registered schema.
    
    MUST Register schema here!
    
    Example Usage:
    
    >>> getSchema( \'LexisNexis\' )
    <__main__.LexisNexisSchema object at 0x022816F0>
    
    
    """
    if( sourceDirectory == settings.LEXISNEXIS_FILETAG ): return LexisNexisSchema()
    raise Exception( "Filer for source <%s> is not registered in getSchema( source )." % ( sourceDirectory ) )

class LexisNexisSchema( object ):
    '''API to normalize IO from uncleaned data to cleaned data
    '''
    class LexisNexisArticleFiler( filers.ArticleFilerBase ):
        '''API to store a LexisNexis Article according to afp.settings
        '''
        paperDateTitleRegex = settings.LEXISNEXIS_REGEX_PAPER_DATE_TITLE
        dateRegex = settings.LEXISNEXIS_REGEX_DATE
        removeFromTitleRegex = settings.LEXISNEXIS_REGEX_EXCLUDE_FROM_TITLE
        schemaName = settings.LEXISNEXIS_FILETAG
        sectionDelimiter = settings.LEXISNEXIS_SECTION_DELIMTER
        removeFromArticleRegex = settings.LEXISNEXIS_REMOVE_FROM_ARTICLE
    
    def getArticleDelimiter( self ):
        return settings.LEXISNEXIS_ARTICLE_DELIMITER
    
    def getArticleFiler( self ):
        return self.LexisNexisArticleFiler()

