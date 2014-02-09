'''
Created on Feb 7, 2014

@author: Christopher Phillippi
'''

import cleaner.retrieve as retrieve
import cleaner.settings as cleanersetttings
import afp.keywords as keywords
import afp.settings as settings
import afp.count as count
import afp.normalize as normalize
import numpy as np


   
def buildTfIdf( articles, keywordMap ):
    counts = count.WordCounter( keywordMap )( articles )
    return normalize.TfIdf()( counts )

if __name__ == "__main__":
    articles = retrieve.getCleanArticles( cleanersetttings.CLEAN_STORE )
    keywordMap = keywords.getKeywordToIndexMap( settings.KEYWORDS_FILEPATH )
    print np.cov( buildTfIdf( articles, keywordMap ))
