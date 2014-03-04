'''
.. module:: cleaner.settings

Contains the constants and settings for the afp package.

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''
from os.path import join
from os.path import expanduser

MASTER_DIR = join( join( expanduser( '~' ), 'Dropbox' ) , 'AFPdb' )
CACHE_DIR = join( MASTER_DIR, 'Cache' )
RESULTS_DIR = join( MASTER_DIR, 'Results' )

KEYWORDS_DIR = join( MASTER_DIR, 'Keywords' )
KEYWORDS_FILEPATH = join( KEYWORDS_DIR, 'keywords.csv' )
