'''
.. module:: settings

Constants and settings for cleaner. Compiled regexes reside here.

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''
from re import compile
from multiprocessing import cpu_count
from os.path import join
from os.path import expanduser

MASTER_DIR = join( expanduser( '~' ), 'AFPdb' )
CLEAN_STORE = join( MASTER_DIR, "Corpus" )  # avoids being saved on dropbox for now
UNCLEAN_STORE = join( MASTER_DIR, "Unclean" )
EMPIRICAL_STORE = join( MASTER_DIR, 'Empirical' )

ADJUSTED_CLOSE_FILENAME = 'adjustedClose.csv'

CLEAN_BATCH_TAG = "cleaned"
CLEAN_BATCH_STORE = join( UNCLEAN_STORE, CLEAN_BATCH_TAG )

MAX_WORKERS = cpu_count()

LEXISNEXIS_ARTICLE_DELIMITER = "All Rights Reserved"
LEXISNEXIS_FILETAG = "LexisNexis"
LEXISNEXIS_REGEX_DATE = compile( "([a-zA-Z]+) ([0-9]+), ([0-9]{4})" )
LEXISNEXIS_REGEX_EXCLUDE_FROM_TITLE = compile( "[:;,'!.\\n]" )
LEXISNEXIS_REGEX_PAPER_DATE_TITLE = compile( "[\\n ]*[0-9]+ of [0-9]+ DOCUMENTS[\\n ]*([\\w'& ]+)[^\\n]*[\\n ]*([a-zA-Z]+ [0-9]+, [0-9]{4}) [:\\w ]*\\n(?:[^\\n]+\\n)*\\n([\\w:;,!.'\\-\\n ]{1,30})" )
LEXISNEXIS_REMOVE_FROM_ARTICLE = compile( "[^\\n]\\n[^\\n]" )
LEXISNEXIS_SECTION_DELIMTER = "\n\n\n"
