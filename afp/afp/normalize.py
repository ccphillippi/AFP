'''
Created on Feb 8, 2014

@author: Christopher Phillippi
'''

class NormalizerBase( object ):
    def __call__( self, matrix ):
        return self.normalize( matrix )
    
    def normalize( self, matrix ):
        NotImplemented
        

class TfIdf( NormalizerBase ):
    def normalize( self, matrix ):
        NotImplemented
