'''
Created on Jan 31, 2014

@author: Christopher Phillippi
@summary: This module contains the lower level API that handles the file system, 
such as saving, cleaning, retrieving files. 
'''

import cleaner.helpers as helpers
             
class BatchFiler( object ):
    '''
    API to retrieve data from a given download batch
    '''
    def __init__( self, schema ):
        self._sourceSchema = schema
        
    def write( self, filename ):
        '''
        Writes a downloaded batch file to the cleaned folder given schema's article filer
        '''
        with open( filename, 'r' ) as f:
            articleFiler = self._sourceSchema.getArticleFiler()
            articles = f.read().split( self._sourceSchema.getArticleDelimiter() )
            return [ articleFiler.write( article ) for article in articles ]
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
        
    def write( self, article ):
        from cleaner import schema
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
        filepath = schema.getFilePath( self._schema, paper.strip(), month, day, year )
        helpers.ensurePath( filepath )
        filename = self.getFileName( title )
        with open( filepath + "\\" + filename, 'w' ) as toFile:
            toFile.write( article.replace( articleOnly, articleReplaced ) )
            return FilerResult( added = True, fileName = filename, filePath = filepath )
        return FilerResult()
    
class FilerResult( object ):
    """
    Result of an attempted article filing
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
                  
    
        
        

