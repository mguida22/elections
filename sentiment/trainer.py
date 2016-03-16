#!/usr/bin/env python3

import random
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews

# create dictionary of features, all words are True for now
def word_feats(words):
    return dict([(word, True) for word in words])

# get pos and neg ids from dataset
negids = movie_reviews.fileids('neg')
posids = movie_reviews.fileids('pos')

# build features
negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]

# shuffle the data
random.shuffle(negfeats)
random.shuffle(posfeats)

# percent cutoff for training and testing
negcutoff = int(len(negfeats) * 0.75)
poscutoff = int(len(posfeats) * 0.75)

# divide dataset into training and testing
trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
print('Training on '+ str(len(trainfeats)) +' instances, tesing on '+ str(len(testfeats)) +' instances')

# build classifier
classifier = NaiveBayesClassifier.train(trainfeats)

# test classifier
print('\nAccuracy: '+ str(nltk.classify.util.accuracy(classifier, testfeats)))
classifier.show_most_informative_features()
