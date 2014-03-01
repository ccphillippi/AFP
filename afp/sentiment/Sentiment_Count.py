'''
import re
import nltk
import pickle
import Clean_Text
#Importing lemmatizer 
#Importing replacers
from random import shuffle
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
print "Classification Done!"

p.close()
n.close()
print "Classification Done!"
'''
##############################################
import nltk
from os import listdir
import string
import csv
import datetime

KeyWord=["google"]
path="/Users/Lee/Dropbox/AFPdb/SparseSent"
Mon=["January","February","March","April","May","June","July","August","September","October","November","December"]
dic_str_to_num=dict(zip(Mon,range(1,13)))
dic_num_to_str=dict(zip(range(1,13),Mon))

d1=datetime.date(2011,1,1)
d2=datetime.date(2013,12,31)
d=[]
for a in range((d2-d1).days+1):
    temp_date=d1+datetime.timedelta(a)
    d.append([str(temp_date.year)+"/"+str(temp_date.month)+"/"+str(temp_date.day),0])
dic=dict(d)

company=listdir(path)
if '.DS_Store' in company: company.remove('.DS_Store')
#fw_occ=open("/Users/Lee/Dropbox/AFPdb/Occurance.csv","w")
#fw_sent=open("/Users/Lee/Dropbox/AFPdb/Sentiment.csv","w")

for c in company:
    print c
'''
    dic_occ=dict(dic)
    dic_sent=dict(dic)
    fr=open(path+"/"+c,"r")
    TXT=fr.readlines()
    fr.close()
    for i in range(len(TXT)):
        TXT[i]=TXT[i].split('@')
    for t in TXT:
        dic_occ[t[0]]+=1
        word=Clean_Text.lemma_Sent(t[1])
        dic_sent[t[0]]+=classifier.prob_classify(Clean_Text.feature_extractor(word)).prob('positive')
    for t in dic_occ.items():
        fw_occ.writelines(str(t[1])+",")
        if t[1]>0:
            fw_sent.writelines(str(dic_sent[t[0]]/t[1])+",")
        else:
            fw_sent.writelines("0,")
    fw_occ.writelines("\n")
    fw_sent.writelines("\n")

fw_occ.close()
'''