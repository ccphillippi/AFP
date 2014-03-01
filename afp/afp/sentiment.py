'''
.. module:: sentiment

.. moduleauthor:: Yu-Ying Lee, Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import nltk
from replacers import RegexReplacer
from replacers import AntonymReplacer
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import pickle

class classifier( object ):
    
    def __init__( self ):
        self.load_classifier()
        self.tokenizer = RegexpTokenizer( "[\w']+" )
        self.lemmatizer = WordNetLemmatizer()
        self.neg_replacer = RegexReplacer()
        self.replacer = AntonymReplacer()
        self.max_key = 300
        self.customstopwords = stopwords.words( 'english' )
        self.customstopwords.remove( "up" )
        self.customstopwords.remove( "down" )
        self.customstopwords += ['s&p500', 'federal', 'united', 'states', 'investors', 'reserve', 'average', 'nikkei' , 'end',
                           'index', 'market', 'cent', 'wall', 'street', 'year', 'years', 'industrial', 'bank_of_america', 'york', 'today',
                           'dow', 'jones', 'it', 'closing', 'closed', 'saw', 'months', 'nasdaq', 'trading', 'us', 'day', 'chase', 'mortgage',
                           'apple', 'say', 'goldman', 'p500', 'microsoft', 'jpmorgan', 'google', 'bank', 'company', 'facebook', 'mr', 'wells_fargo',
                           'share', 'quarter', 'week', 'sachs', 'executive', 'yesterday', 'investor', 'executive', 'yesterday', 'investor', 'earnings', 'time', 'service', 'month', 'bank_of_america', 'business']
        
    def set_Wordlist( self, tweets ):
        # Calls above functions - gives us list of the words in the tweets, ordered by freq.
        wordlist = self.getwordfeatures( self.getwords( tweets ) )
        wordlist = [ i for i in wordlist if not i in self.customstopwords ]
        wordlist = wordlist[ :self.max_key ]
        f = open( "WordList.txt", 'w' )
        pickle.dump( wordlist, f )
        return wordlist
    
    # Pull out all of the words in a list of tagged tweets, formatted in tuples.
    def getwords( self, tweets ):
        allwords = []
        for ( words, _ ) in tweets:
            allwords.extend( words )
        return allwords
    
    # Order a list of tweets by their frequency.
    def getwordfeatures( self, listoftweets ):
    # Print out wordfreq if you want to have a look at the individual counts of words.
        wordfreq = nltk.FreqDist( listoftweets )
        words = wordfreq.keys()
        return words
    
    def feature_extractor( self, doc ):
        docwords = set( doc )
        features = {}
        for i in self.wordlist:
            features['contains(%s)' % i] = ( i in docwords )
        return features
    
    def sent_prob( self, sentence ):
        temp = self.lemma_Sent( sentence )
        print str( classifier.prob_classify( self.feature_extractor( temp ) ).prob( 'positive' ) )
    
    def lemma_Sent( self, doc ):
        doc = self.neg_replacer.replace( doc )
        word = self.tokenizer.tokenize( doc )
        word_pos = nltk.pos_tag( word )
    #    replacer.replace_negations_pos(word_pos)
        dic = dict( word_pos )
          
        word_lemma = []    
        for i in zip( *word_pos )[0]:
            if dic[i] == None:
                pass
            elif dic[i][0] == "V":
                word_lemma.append( self.lemmatizer.lemmatize( i, "v" ).lower() )
            elif dic[i][0] == "N" or dic[i][0] == "ADJ" or dic[i][0] == "ADV":
                word_lemma.append( self.lemmatizer.lemmatize( i ).lower() ) 
        return word_lemma
    
    def load_classifier( self ):
        f = open( "Classifier.dump", 'r' )
        self.classifier = pickle.load( f )
        f.close()
        f = open( "WordList.txt", 'r' )
        self.wordlist = pickle.load( f )
        f.close()
    
            
