'''
Created on Feb 7, 2014

@author: Christopher Phillippi
'''

import cleaner
import afp
from afp import count
from afp import normalize

   
def buildTfIdf( articles, keywords ):
    return normalize.TfIdf( count.WordCounter( keywords )( articles ) )

if __name__ == "__main__":
    articles = cleaner.retrieve.getCleanArticles( cleaner.settings.CLEAN_STORE )
    keywords = afp.keywords.getAliasToKeywordMap( afp.settings.KEYWORDS_FILEPATH )
    tfidf = buildTfIdf( articles, keywords )
