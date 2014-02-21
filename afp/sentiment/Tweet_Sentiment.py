import nltk
import math
import re
import sys
import os
import codecs
reload(sys)
sys.setdefaultencoding('utf-8')

from nltk.corpus import stopwords

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

postweet = __location__ + "/postweets.txt"
negtweet = __location__ + "/negtweets.txt"


customstopwords = ['band', 'they', 'them']

#Load positive tweets into a list
p = open(postweet, 'r')
postxt = p.readlines()

#Load negative tweets into a list
n = open(negtweet, 'r')
negtxt = n.readlines()
print "Positive Lines:" + str(len(negtxt))

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

tweets = []

#Create a list of words in the tweet, within a tuple.
for (word, sentiment) in taggedtweets:
    word_filter = [i.lower() for i in word.split()]
    tweets.append((word_filter, sentiment))

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
print getwordfeatures(getwords(tweets))

wordlist = getwordfeatures(getwords(tweets))
wordlist = [i for i in wordlist if not i in stopwords.words('english')]
wordlist = [i for i in wordlist if not i in customstopwords]

def feature_extractor(doc):
    docwords = set(doc)
    features = {}
    for i in wordlist:
        features['contains(%s)' % i] = (i in docwords)
    return features

#Creates a training set - classifier learns distribution of true/falses in the input.

training_set = nltk.classify.apply_features(feature_extractor, tweets)
print tweets
print training_set

classifier = nltk.NaiveBayesClassifier.train(training_set)

print classifier.show_most_informative_features(n=30)

while True:
    input = raw_input('ads')
    if input == 'exit':
        break
    elif input == 'informfeatures':
        print classifier.show_most_informative_features(n=30)
        continue
    else:
        input = input.lower()
        input = input.split()
        print '\nWe think that the sentiment was ' + classifier.classify(feature_extractor(input)) + ' in that sentence.\n'
        print input
p.close()
n.close()