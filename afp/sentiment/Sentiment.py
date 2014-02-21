import pickle
from replacers import RegexReplacer
from replacers import AntonymReplacer
import nltk
from nltk.tokenize import RegexpTokenizer
tokenizer =RegexpTokenizer("[\w']+")
neg_replacer=RegexReplacer()
replacer=AntonymReplacer()
#Importing lemmatizer 
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()


f=open("Classifier.dump",'r')
classifier=pickle.load(f)
f.close()
print classifier
f=open("WordList.txt",'r')
wordlist=pickle.load(f)
f.close()
print wordlist

def feature_extractor(doc):
    docwords = set(doc)
    features = {}
    for i in wordlist:
        features['contains(%s)' % i] = (i in docwords)
    return features

'''
def feature_extractor(doc):
    #doc=neg_replacer.replace(doc)
    word_filter=tokenizer.tokenize(doc)
    
    #word_pos=nltk.pos_tag(word_filter)
    #replacer.replace_negations_pos(word_pos)
    #word_lemma=[]
    
    #dic=dict(word_pos)
    
    for i in zip(*word_pos)[0]:
        if dic[i]==None:
            pass
        elif dic[i][0]=="V":
            word_lemma.append(lemmatizer.lemmatize(i, "v").lower())
        elif dic[i][0]=="N" or dic[i][0]=="ADJ" or dic[i][0]=="ADV":
            word_lemma.append(lemmatizer.lemmatize(i).lower()) 
    
    #docwords = set(word_lemma)
    #docwords = set(zip(*word_pos)[0])
    
    features = {}
    for i in wordlist:
        features['contains(%s)' % i] = (i in word_filter)
    
    return features
'''
print "Loading Classification Done."
#print classifier.show_most_informative_features(n=30)


f=open('SP_Sent.txt','rU')
TXT=f.readlines()

for i in TXT:
    print 'Prob: ' + str(classifier.prob_classify(feature_extractor(i)).prob('positive') )


    #Inputing New Sentence
'''
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
        print '\nWe think that the sentiment was ' + classifier.classify(feature_extractor(input)) + ' in that sentence.'
        print input
        print feature_extractor(input)
        print classifier.prob_classify(feature_extractor(input)).prob('positive')
  

p.close()
n.close()
    
    
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
    print classifier.prob_classify(feature_extractor(input)).prob('positive')

'''