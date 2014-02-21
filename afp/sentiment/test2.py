import nltk

#Importing lemmatizer 
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

#Importing replacers
from replacers import AntonymReplacer
replacer=AntonymReplacer()
from nltk.tokenize import RegexpTokenizer
tokenizer =RegexpTokenizer("[\w']+")

#Importing Chunkers
patterns = """ 
 NP: {<DT|PP\$>?<JJ>*<NN>} 
 {<NNP>+} 
 {<NN>+} 
""" 
#chunker=nltk.RegexpParser(patterns)
import chunkers
import pickle
#from nltk.corpus import treebank_chunk
#chunker=chunkers.TagChunker(treebank_chunk.chunked_sents())
f=open("chunker.dump",'r')
chunker=pickle.load(f) 
 
# training the chunker, ChunkParser is a class defined in the next slide 
#NPChunker = ChunkParser(train_sents) 
TxT="This method doesn't work well, because xxx."
from replacers import RegexReplacer
neg_replacer=RegexReplacer();
TxT=neg_replacer.replace(TxT)
sent=nltk.pos_tag(nltk.word_tokenize(TxT))
#tree=chunker.parse(sent)
#print "SubTree"
#subtree=replacer.FindSubTree(tree, 'not', 'work')
#print subtree
print "After Negation"
replacer.replace_negations_pos(sent)
print sent