'''
Created on Feb 7, 2014

@author: Christopher Phillippi
@summary: Stores schema configurations, both for unclean and clean schemas
'''

import cleaner.filers as filers
import cleaner.settings as settings

#======================================
# Clean Schema
#======================================
def getFilePath( source, paper, month, day, year ):
    """
    Configures cleaned file system schema
    """
    return "\\".join( [ settings.CLEAN_STORE, source, year, month, day, paper ] )


#======================================
# Dirty Schemas
#======================================
def getSchema( sourceDirectory ):
    """
    Given a sourceDirectory, returns the registered schema
    for example: LexisNexis -> LexisNexis Schema Object
    
    MUST Register schema here!
    """
    if( sourceDirectory == settings.LEXISNEXIS_FILETAG ): return LexisNexisSchema()
    raise Exception( "Filer for source <%s> is not registered in getSchema( source )." % ( sourceDirectory ) )

class LexisNexisSchema( object ):
    '''
    API to normalize IO from uncleaned data to cleaned data
    '''
    class LexisNexisArticleFiler( filers.ArticleFilerBase ):
        '''
        API to store a LexisNexis Article according to afp.settings
        '''
        paperDateTitleRegex = settings.LEXISNEXIS_REGEX_PAPER_DATE_TITLE
        dateRegex = settings.LEXISNEXIS_REGEX_DATE
        removeFromTitle = settings.LEXISNEXIS_REGEX_EXCLUDE_FROM_TITLE
        schema = settings.LEXISNEXIS_FILETAG
        sectionDelimiter = settings.LEXISNEXIS_SECTION_DELIMTER
        removeFromArticle = settings.LEXISNEXIS_REMOVE_FROM_ARTICLE
    
    def getArticleDelimiter( self ):
        return settings.LEXISNEXIS_ARTICLE_DELIMITER
    
    def getArticleFiler( self ):
        return self.LexisNexisArticleFiler()
