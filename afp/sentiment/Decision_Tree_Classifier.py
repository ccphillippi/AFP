import re
import nltk
import pickle

#Importing lemmatizer 
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

#Importing tagger
from nltk.tag import UnigramTagger
from nltk.corpus import treebank
train_sents = treebank.tagged_sents()
tagger=UnigramTagger(train_sents)

#Importing replacers
from replacers import RegexReplacer
from replacers import AntonymReplacer
replacer=RegexReplacer()
from nltk.tokenize import RegexpTokenizer
tokenizer =RegexpTokenizer("[\w']+")
from random import shuffle


#Importing Chunkers
import chunkers
from nltk.corpus import treebank_chunk
chunker=chunkers.TagChunker(treebank_chunk.chunked_sents())


max_key=100
customstopwords = stopwords.words('english')
customstopwords.remove("up")
customstopwords.remove("down")
customstopwords += ['s&p500','federal','united','states','investors', 'reserve', 'average', 'nikkei' ,'end',
                   'index','market','cent','wall','street','year','years','industrial',
                   'dow','jones','it','closing','closed','saw','months','nasdaq','trading','us','day','chase','mortgage']

#Load positive tweets into a list
p = open('postweets2.txt', 'r')
postxt = p.readlines()

#Load negative tweets into a list
n = open('negtweets2.txt', 'r')
negtxt = n.readlines()

neglist = []
poslist = []

#Create a list of 'negatives' with the exact length of our negative tweet list.
for i in range(0,len(negtxt)):
    neglist.append('negative')

#Likewise for positive.
for i in range(0,len(postxt)):
    poslist.append('positive')

#Creates a list of tuples, with sentiment tagged.
postagged = zip(postxt, poslist)
negtagged = zip(negtxt, neglist)

#Combines all of the tagged tweets to one large list.
taggedtweets = postagged + negtagged
shuffle(taggedtweets)
tweets = []

#Create a list of words in the tweet, within a tuple.
for (word, sentiment) in taggedtweets:
    word_filter=tokenizer.tokenize(word)
    word_filter=AntonymReplacer().replace_negations(word_filter)
    dic=dict(tagger.tag(word_filter))
    
    word_lemma=[]
    
    for i in word_filter:
        if dic[i]==None:
            pass
        elif dic[i][0]=="V":
            word_lemma.append(lemmatizer.lemmatize(i, "v").lower())
        elif dic[i][0]=="N" or dic[i][0]=="ADJ" or dic[i][0]=="ADV":
            word_lemma.append(lemmatizer.lemmatize(i).lower()) 
    tweets.append((word_lemma, sentiment))


#Pull out all of the words in a list of tagged tweets, formatted in tuples.
def getwords(tweets):
    allwords = []
    for (words, sentiment) in tweets:
        allwords.extend(words)
    return allwords

#Order a list of tweets by their frequency.
def getwordfeatures(listoftweets):
#Print out wordfreq if you want to have a look at the individual counts of words.
    wordfreq = nltk.FreqDist(listoftweets)
    words = wordfreq.keys()
    return words

#Calls above functions - gives us list of the words in the tweets, ordered by freq.

wordlist = getwordfeatures(getwords(tweets))
wordlist = [i for i in wordlist if not i in customstopwords]
wordlist = wordlist[:max_key]

def feature_extractor(doc):
    docwords = set(doc)
    features = {}
    for i in wordlist:
        features[i] = (i in docwords)
    return features

#Creates a training set - classifier learns distribution of true/falses in the input.
#training_set = nltk.classify.apply_features(feature_extractor, tweets)
whole_set = nltk.classify.apply_features(feature_extractor, tweets)
N_Set=len(whole_set)
testing_set= whole_set[:N_Set/5]
training_set= whole_set[N_Set/5:]

#classifier = nltk.classify.DecisionTreeClassifier.train(training_set )
classifier = nltk.classify.MaxentClassifier.train(training_set,algorithm='gis',trace=0,max_iter=10)
#precision,recall = nltk.classify.precision_recall(classifier,testing_set)
#print precision('pos')
print nltk.classify.accuracy(classifier,testing_set )

print classifier

print "Classification Done!"
#print classifier.show_most_informative_features(n=30)


#f=open("Classifier.dump",'w')
#pickle.dump(classifier,f)

#f=open("WordList.txt",'w')
#pickle.dump(wordlist,f)

p.close()
n.close()
