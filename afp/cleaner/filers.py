'''
Created on Jan 31, 2014

@author: Christopher Phillippi
@summary: This module contains the code that handles the file system, 
such as saving, cleaning, retrieving files. A call to 
cleanSources() or getCleanArticles() should be about all you need
from this module. The remaining functions and classes allow for additional
schemas to be implemented, say other than LexisNexis. See the LexisNexis class
for an example of how to create a Schema.
'''
from cleaner import settings
import multiprocessing as mp
import errno, os

def cleanSources( uncleanStore, numWorkers = settings.MAX_WORKERS ):
    """
    Cleans all files in unclean directory, using numWorkers processors
    Call this function directly to clean data
    """
    pool = mp.Pool( numWorkers )
    print "Cleaning data in <%s> with <%d> workers." % ( uncleanStore, numWorkers )
    
    def clean( source ):
        try:
            filer = DownloadFiler( getSchema( source ) )
        except Exception as e:
            return [e]
        sourceDir = os.path.join( settings.UNCLEAN_STORE, source )
        uncleaned = ( ( filer, sourceDir, uncleaned ) for uncleaned in os.listdir( sourceDir ) )
        return pool.map( cleanFile, uncleaned )
    results = flatten( [ clean( source ) for source in os.listdir( uncleanStore ) ] )
    added = [ result for result in results if result.added  ]
    notAdded = [ result for result in results if not result.added ]
    return { "Added" : added, "Unable To Add" : notAdded }

def getFilePath( source, paper, month, day, year ):
    """
    Configures cleaned file system schema
    """
    return "\\".join( [ settings.CLEAN_STORE, source, year, month, day, paper.strip() ] )

def ensurePath( filepath ):
    """
    Helper function to create a path if it doesn't not currently exist, else does nothing
    """
    try:
        os.makedirs( filepath )
    except OSError as e:
        if( e.errno == errno.EEXIST and os.path.isdir( filepath ) ): pass
        else: raise


def flatten( x ):
    """
    Helper function to flatten iterables of iterables of ...
    """
    if isinstance( x, str ):
        return [ x ];
    try:
        return [ a for i in x for a in flatten( i ) ]
    except:
        return [ x ]

def getSchema( sourceDirectory ):
    """
    Given a sourceDirectory, returns the registered schema
    for example: LexisNexis -> LexisNexis Schema Object
    """
    if( sourceDirectory == settings.LEXISNEXIS_FILETAG ): return LexisNexisSchema()
    raise Exception( "Filer for source <%s> is not registered in getSchema( source )." % ( sourceDirectory ) )

# Multithreading library requires this be a function rather than method or inner function
# Unpickleable otherwise
def cleanFile( args ):
    filer, cleanDir, uncleanFile = args
    return filer.write( os.path.join( cleanDir, uncleanFile ) )
             

class FilerResult( object ):
    """
    Result of a batch clean
    """
    def __init__( self, added = None, article = None, fileName = None, filePath = None ):
        self.added = added
        self.article = article
        self.fileName = fileName
        self.filePath = filePath
    def __str__( self ):
        if self.added: return "<%s> in <%s>" % ( self.fileName, self.filePath )
        elif ( self.added is False ): return "%s" % self.article
        else: return "Unknown: %s" % self.article
    def __repr__( self ):
        return self.__str__()        

class DownloadFiler( object ):
    '''
    API to retrieve data from a given download
    '''
    _sourceSchema = None

    def __init__( self, schema ):
        self._sourceSchema = schema
        
    def write( self, filename ):
        '''
        Writes a downloaded file to the cleaned folder given schema's article filer
        '''
        with open( filename, 'r' ) as f:
            articleFiler = self._sourceSchema.getArticleFiler()
            articles = f.read().split( self._sourceSchema.getArticleDelimiter() )
            return [ articleFiler.toFileSystem( article ) for article in articles ]
        raise Exception( "Unable to open file for read: <%s>." % filename )
                
                
class ArticleFilerBase( object ):
    '''
    Base API to store an article according to regex members
    '''
    _paperDateTitleRegex = None
    _dateRegex = None
    _removeFromTitle = None
    _schema = None
    _sectionDelimiter = None
    _removeFromArticle = None
    
    def getFileName( self, title ):
            return self._removeFromTitle.sub( "", title.strip() ).replace( " ", "_" ) + ".txt"
        
    def toFileSystem( self, article ):
        def getArticleOnly():
            sections = article.split( self._sectionDelimiter )
            lengths = [ len( section ) for section in sections ]
            sectionByLength = dict( zip( lengths, sections ) )
            return sectionByLength[ max( lengths ) ]  # assume article has maximum length
        
        try:
            paper, date, title = self._paperDateTitleRegex.search( article ).groups()
        except:
            return FilerResult( False, article = article )
        articleOnly = getArticleOnly()
        articleReplaced = self._removeFromArticle.sub( lambda match : match.group().replace( "\n", " " ), articleOnly )
        month, day, year = self._dateRegex.search( date ).groups()
        filepath = getFilePath( self._schema, paper, month, day, year )
        ensurePath( filepath )
        filename = self.getFileName( title )
        with open( filepath + "\\" + filename, 'w' ) as toFile:
            toFile.write( article.replace( articleOnly, articleReplaced ) )
            return FilerResult( added = True, fileName = filename, filePath = filepath )
        return FilerResult()
        
class LexisNexisSchema( object ):
    '''
    API to normalize IO from uncleaned data to cleaned data
    '''
    class LexisNexisArticleFiler( ArticleFilerBase ):
        '''
        API to store a LexisNexis Article according to afp.settings
        '''
        _paperDateTitleRegex = settings.LEXISNEXIS_REGEX_PAPER_DATE_TITLE
        _dateRegex = settings.LEXISNEXIS_REGEX_DATE
        _removeFromTitle = settings.LEXISNEXIS_REGEX_EXCLUDE_FROM_TITLE
        _schema = settings.LEXISNEXIS_FILETAG
        _sectionDelimiter = settings.LEXISNEXIS_SECTION_DELIMTER
        _removeFromArticle = settings.LEXISNEXIS_REMOVE_FROM_ARTICLE
    
    def getArticleDelimiter( self ):
        return settings.LEXISNEXIS_ARTICLE_DELIMITER
    
    def getArticleFiler( self ):
        return self.LexisNexisArticleFiler()
                          
if __name__ == '__main__':
    cleanSources( settings.UNCLEAN_STORE )
        
        

