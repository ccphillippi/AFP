'''
.. module:: filers

This module contains the lower level API that handles the storing to the filesystem

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
   
'''

import helpers as helpers
             
class BatchFiler( object ):
    '''API to retrieve data from a given download batch
    '''
    def __init__( self, schema ):
        """
        :param schemaName: Schema object from :mod:`cleaner.schemaName`
        """
        self._sourceSchema = schema
        
    def write( self, filename ):
        '''Writes a downloaded batch file to the cleaned folder given schemaName's article filer
        
        :param filename: Filename of batch to read from.
        '''
        with open( filename, 'r' ) as f:
            articles = f.read().split( self._sourceSchema.getArticleDelimiter() )
            return self.writeAll( articles )  # [ articleFiler.write( article ) for article in articles ]
        raise Exception( "Unable to open file for read: <%s>." % filename )
    
    def writeAll( self, articles ):
        articleFiler = self._sourceSchema.getArticleFiler()
        return [ articleFiler.write( article ) for article in articles ]

class CouchDBFiler( BatchFiler ):
    def __init__( self, dbName = 'articles', server = 'http://localhost:5984', *args, **kwargs ):
        self.dbName = dbName
        self.server = server
        print 'Unused Args: %s' % args
        print 'Unused Keywords: %s' % kwargs
        
    def writeAll( self, articles ):
        import couchdb
        db = couchdb.Server( self.server )
        try:
            db.update( articles, all_or_nothing = True )
        except:
            return[ FilerResult( added = False, article = article ) for article in articles ]
        else:
            return [ FilerResult( added = True, filename = self.dbName, filepath = self.server ) for _ in articles ]
        
                
class ArticleFilerBase( object ):
    '''Base API to store an article according to regex members. Use this as a base for custom schema. See :class:`cleaner.schema.LexisNexisSchema` as an example.
    
    :member paperDateTitleRegex: Regex retrieving ( paper, date, title ), compiled with :py:func:`re.compile`
    :member dateRegex: Regex retrieving ( month, day, year ), compiled with :py:func:`re.compile`
    :member removeFromTitleRegex: Regex class of any letter to be removed from the article title, compiled with :py:func:`re.compile`
    :member removeFromArticleRegex: Regex retrieving newlines in sentences, compiled with :py:func:`re.compile`
    :member schemaName: Name of schema to use, should be the same as one registered in :py:func:`cleaner.schema.getSchema`
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
    
    def parse( self, article ):
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
        
        return dict( 
            date = dict( 
                month = month,
                day = day,
                year = year,
            ),
            body = article.replace( articleOnly, articleReplaced ),
            title = title.strip(),
            paper = paper.strip(),
        )
            
        
    def write( self, article ):
        from cleaner import schema
        parsed = self.parse( article )
        date, title = map( parsed.get, [ 'date', 'title' ] )
        month, day, year = map( date.get, [ 'month', 'date', 'year' ] )
        filepath = schema.getFilePath( self.schemaName, parsed[ 'paper' ], month, day, year )
        helpers.ensurePath( filepath )
        filename = self.getFileName( title )
        with open( filepath + "\\" + filename, 'w' ) as toFile:
            toFile.write( parsed[ 'body' ] )
            return FilerResult( added = True, fileName = filename, filePath = filepath )
        return FilerResult()
        
    
class FilerResult( object ):
    """Result of an attempted article filing
    
    Prints as:
        - file and filepath if successful
        - the article if failed to store
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
                  
    
        
        

