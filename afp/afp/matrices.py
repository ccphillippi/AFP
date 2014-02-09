'''
.. module:: matrices

This module contains the matrix generating functions

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import cleaner.retrieve as retrieve
import cleaner.settings as cleanersettings
import afp.keywords as keywords
import afp.settings as settings
import afp.count as count
import afp.normalize as normalize
import numpy as np


   
def tfIdf( articles, keywordMap ):
    """Returns a dense tf-idf Matrix
    
    TODO: Find sparse matrix library that allows more sparse flexibility to avoid dense matrix return
    
    :param articles: An iterable of article strings. See :func:`cleaner.retrieve.getCleanArticles`
    :param keywordMap: A mapping of keywords to their matrix column indices. See :func:`afp.keywords.getKeywordToIndexMap`
    """
    counts = count.WordCounter( keywordMap )( articles )
    return normalize.TfIdf()( counts )

if __name__ == "__main__":
    articles = retrieve.getCleanArticles( cleanersettings.CLEAN_STORE )
    keywordMap = keywords.getKeywordToIndexMap( settings.KEYWORDS_FILEPATH )
    print np.cov( tfIdf( articles, keywordMap ) )
