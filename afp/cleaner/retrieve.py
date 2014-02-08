'''
Created on Feb 7, 2014

@author: Christopher Phillippi
@summary: High level API to retrieve cleaned files
'''

import cleaner.settings as settings
import os

def getCleanArticles( cleanStore ):
    """
    Returns iterable of all cleaned articles
    """
    def getArticle( f ):
        with open( f, 'r' ) as opened:
            article = opened.read()
        return article
    return ( getArticle( f ) for f in getCleanFileList( cleanStore ) )

def getCleanFileList( cleanStore ):
    """
    Returns interable of all cleaned files
    """    
    directory = ( os.path.join( cleanStore, f ) for f in os.listdir( cleanStore ) )
    for f in directory:
        if os.path.isfile( f ):
            yield f
        else:
            for subFile in getCleanFileList( f ):
                yield subFile


if __name__ == "__main__":
    files = getCleanFileList( settings.CLEAN_STORE )
    for f in files:
        print f
