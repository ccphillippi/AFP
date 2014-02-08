'''
Created on Jan 31, 2014

@author: Christopher Phillippi
@summary: Constants and settings for cleaner
'''
from re import compile
from multiprocessing import cpu_count
import os


CLEAN_STORE = "C:\\AFPcorpus" #avoids being saved on dropbox for now
UNCLEAN_STORE = os.path.abspath( "unclean" )

MAX_WORKERS = cpu_count()

LEXISNEXIS_ARTICLE_DELIMITER = "All Rights Reserved"
LEXISNEXIS_FILETAG = "LexisNexis"
LEXISNEXIS_REGEX_DATE = compile( "([a-zA-Z]+) ([0-9]+), ([0-9]{4})" )
LEXISNEXIS_REGEX_EXCLUDE_FROM_TITLE = compile( "[:;,'!.\\n]" )
LEXISNEXIS_REGEX_PAPER_DATE_TITLE = compile( "[\\n ]*[0-9]+ of [0-9]+ DOCUMENTS[\\n ]*([\\w'& ]+)[^\\n]*[\\n ]*([a-zA-Z]+ [0-9]+, [0-9]{4}) [:\\w ]*\\n(?:[^\\n]+\\n)*\\n([\\w:;,!.'\\-\\n ]{1,30})" )
LEXISNEXIS_REMOVE_FROM_ARTICLE = compile( "[^\\n]\\n[^\\n]" )
LEXISNEXIS_SECTION_DELIMTER = "\n\n\n"
