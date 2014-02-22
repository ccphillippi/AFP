'''
.. module:: cleaner.settings

Contains the constants and settings for the afp package.

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''
from os.path import join
from os.path import expanduser

MASTER_DIR = join( expanduser( '~' ), 'AFPdb' )
KEYWORDS_FILEPATH = join( MASTER_DIR, 'Keywords/keywords.csv' )
