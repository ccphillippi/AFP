'''
Created on Feb 8, 2014

@author: Christopher Phillippi
'''

import numpy as np
from itertools import chain

class NormalizerBase( object ):
    def __call__( self, raw ):
        return self.normalize( raw )
    
    def normalize( self, matrix ):
        NotImplemented
        

class TfIdf( NormalizerBase ):
    def normalize( self, counts ):
        n = counts.shape[ 0 ]
        absCounts = np.abs( counts )
        def tf():
            return counts.sign().multiply( absCounts.log1p() )
        def idf():
            occurred = ( absCounts > 0 ).asfptype()
            occurrences = sum( occurred, 0 ).todense() 
            occurrences[ occurrences == 0 ] = 1
            return np.log( float( n ) / occurrences )
        return tf().multiply( idf() )
    
class Article( NormalizerBase ):
    wordReplacements = [ 
                         ( '\'s', "" ),
                         ( 'n\'t', " not" ),
                         ( "/", " or " ),
                       ]
        
    def normalize( self, article ):
        def getPossibleKeywords( line ):
            def normalizeKeyword( word ):
                def replaceFromTo( interWord, fromTo ):
                    replFrom, to = fromTo
                    return interWord.replace( replFrom, to )
                return reduce( replaceFromTo, self.wordReplacements, word )
            return ( normalizeKeyword( word ) for word in line.split( " " ) )
        return chain.from_iterable( ( getPossibleKeywords( line ) 
                                      for line in article.lower().split( "\n" ) ) )
        
        
        
