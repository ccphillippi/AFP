'''
.. module:: matrices

This module contains the matrix generating functions

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import cleaner.retrieve as retrieve
import afp.keywords as keywords
import afp.count as count
import afp.normalize as normalize
import afp.linalg as linalg
import afp.settings as settings
import numpy as np
   
def tfIdf( articles, keywordsFilePath = settings.KEYWORDS_FILEPATH ):
    """Returns a sparse tf-idf Matrix
    
    :param articles: An iterable of article strings. See :func:`cleaner.retrieve.getCleanArticles`
    :param keywordsFilePath: Path to *keywords.csv*
    :type keywordsFilePath: str
    """
    keywordMap = keywords.getKeywordToIndexMap( keywordsFilePath );
    counts = count.WordCounter( keywordMap )( articles )
    return normalize.TfIdf()( counts )

if __name__ == "__main__":
    corr = linalg.corr( tfIdf( retrieve.getCleanArticles() ) )
    np.savetxt( settings.RESULTS_DIR + '/corr2012.csv', corr, delimiter = ',' )
