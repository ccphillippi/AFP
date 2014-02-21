import re
import nltk
import pickle
import Clean_Text
#Importing lemmatizer 


#Importing tagger
#from nltk.tag import UnigramTagger
#from nltk.corpus import treebank
#train_sents = treebank.tagged_sents()
#tagger=UnigramTagger(train_sents)

#Importing replacers
from random import shuffle


#Importing Chunkers
#import chunkers
#from nltk.corpus import treebank_chunk
#chunker=chunkers.TagChunker(treebank_chunk.chunked_sents())

#Importing Classification
from classification import precision_recall


#Load positive tweets into a list
p = open('postweets2.txt', 'r')
postxt = p.readlines()

print "Positive Lines:" + str(len(postxt))
#Load negative tweets into a list
n = open('negtweets2.txt', 'r')
negtxt = n.readlines()
negtxt += negtxt[:101]
print "Negative Lines:" + str(len(negtxt))
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
    tweets.append((Clean_Text.lemma_Sent(word), sentiment))
   
Clean_Text.wordlist=Clean_Text.set_Wordlist(tweets)

#Creates a training set - classifier learns distribution of true/falses in the input.
#training_set = nltk.classify.apply_features(feature_extractor, tweets)
whole_set = nltk.classify.apply_features(Clean_Text.feature_extractor, tweets)

N_Set=len(whole_set)

#testing_set= whole_set[:N_Set/5]
#training_set= whole_set[N_Set/5:]
testing_set=whole_set
training_set=whole_set

classifier = nltk.classify.NaiveBayesClassifier.train(training_set)
print "Accuracy:" +str(nltk.classify.accuracy(classifier,testing_set))

precision, recall = precision_recall(classifier, testing_set )

print precision['positive']
print precision['negative']
print recall['positive']
print recall['negative']

print "Classification Done!"
print classifier.show_most_informative_features(50)


f=open("Classifier.dump",'w')
pickle.dump(classifier,f)

p.close()
n.close()
f.close()


f=open('SP_Sent.txt','rU')
TXT=f.readlines()

for i in TXT:
    i=i.replace("\n",'')
    i=Clean_Text.lemma_Sent(i)
    print str(classifier.prob_classify(Clean_Text.feature_extractor(i)).prob('positive') )



'''
while True:
    input = raw_input("Please write a sentence to be tested for sentiment. If you type 'exit', the program will quit. If you want to see the most informative features, type informfeatures.\n")
    if input == 'exit':
        break
    elif input == 'informfeatures':
        print classifier.show_most_informative_features(n=30)
        continue
    else:
        input = input.lower()
        input = input.split()
    print feature_extractor(input)
    print 'We think that the sentiment was ' + classifier.classify(feature_extractor(input)) + ' in that sentence.'
    print input
    print "\n"
'''
