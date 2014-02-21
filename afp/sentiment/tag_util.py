from nltk.tag import RegexpTagger, UnigramTagger
from nltk.corpus import brown

patterns = [
    (r'^@\w+', 'NNP'),
    (r'^\d+$', 'CD'),
    (r'.*ing$', 'VBG'),
    (r'.*ment$', 'NN'),
    (r'.*ful$', 'JJ'),
    (r'.*', 'NN')
]
re_tagger = RegexpTagger(patterns)
tagger = UnigramTagger(brown.tagged_sents(), backoff=re_tagger) # train tagger

def backoff_tagger(train_sents, tagger_classes, backoff=None):
    for cls in tagger_classes:
        backoff = cls(train_sents, backoff=backoff)
    return backoff