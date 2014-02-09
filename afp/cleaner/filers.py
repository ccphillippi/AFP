'''
.. module:: filers

:synopsis: This module contains the lower level API that handles the storing to the filesystem

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
   
'''

import cleaner.helpers as helpers
             
class BatchFiler( object ):
    '''API to retrieve data from a given download batch
    '''
    def __init__( self, schema ):
        """
        :param schemaName: Schema object from :mod:'cleaner.schemaName'
        """
        self._sourceSchema = schema
        
    def write( self, filename ):
        '''Writes a downloaded batch file to the cleaned folder given schemaName's article filer
        
        :param filename: Filename of batch to read from.
        '''
        with open( filename, 'r' ) as f:
            articleFiler = self._sourceSchema.getArticleFiler()
            articles = f.read().split( self._sourceSchema.getArticleDelimiter() )
            return [ articleFiler.write( article ) for article in articles ]
        raise Exception( "Unable to open file for read: <%s>." % filename )
                
class ArticleFilerBase( object ):
    '''Base API to store an article according to regex members. Use this as a base for custom schema. See :class:'cleaner.schema.LexisNexisSchema' as an example.
    
    :member paperDateTitleRegex: Regex retrieving ( paper, date, title ), compiled with :func:'re.compile'
    :member dateRegex: Regex retrieving ( month, day, year ), compiled with :func:'re.compile'
    :member removeFromTitleRegex: Regex class of any letter to be removed from the article title, compiled with :func:'re.compile'
    :member removeFromArticleRegex: Regex retrieving newlines in sentences, compiled with :func:'re.compile'
    :member schemaName: Name of schema to use, should be the same as one registered in :func:'cleaner.schema.getSchema'
    :member sectionDelimiter: String to use as delimiter between sections of the article.
    '''
    paperDateTitleRegex = None
    dateRegex = None
    removeFromTitleRegex = None
    removeFromArticleRegex = None
    schemaName = None
    sectionDelimiter = None
    
    def getFileName( self, title ):
        """Processes filename for article to be stored
        
        :param title: Article title to be incorporated in filename.
        """
        return self.removeFromTitleRegex.sub( "", title.strip() ).replace( " ", "_" ) + ".txt"
        
    def write( self, article ):
        from cleaner import schema
        def getArticleOnly():
            sections = article.split( self.sectionDelimiter )
            lengths = [ len( section ) for section in sections ]
            sectionByLength = dict( zip( lengths, sections ) )
            return sectionByLength[ max( lengths ) ]  # assume article has maximum length
        
        try:
            paper, date, title = self.paperDateTitleRegex.search( article ).groups()
        except:
            return FilerResult( False, article = article )
        articleOnly = getArticleOnly()
        articleReplaced = self.removeFromArticleRegex.sub( lambda match : match.group().replace( "\n", " " ), articleOnly )
        month, day, year = self.dateRegex.search( date ).groups()
        filepath = schema.getFilePath( self.schemaName, paper.strip(), month, day, year )
        helpers.ensurePath( filepath )
        filename = self.getFileName( title )
        with open( filepath + "\\" + filename, 'w' ) as toFile:
            toFile.write( article.replace( articleOnly, articleReplaced ) )
            return FilerResult( added = True, fileName = filename, filePath = filepath )
        return FilerResult()
    
class FilerResult( object ):
    """Result of an attempted article filing
    
    Prints as:
        - file and filepath if successful
        - the article if failed to store
        
    :members:
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
                  
    
        
        

