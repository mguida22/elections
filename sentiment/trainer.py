#! /usr/bin/env python3

import csv
import os
import sys
from nltk.classify import NaiveBayesClassifier

import utils


# the number of tweets per category to add to the trimmed set.
# set at 400000 for all tweets, lower if you want the training to go faster
INFILE = 'training_set.csv'
LIMIT = 400000

# take in args if available
if len(sys.argv) == 2:
    INFILE = str(sys.argv[1])
elif len(sys.argv) == 3:
    INFILE = str(sys.argv[1])
    LIMIT = int(sys.argv[2])

print('Triming to {0} tweets per category'.format(LIMIT))
print('This may take a long time.')

posCount = 0
negCount = 0

outfile = open('trimmed.csv', 'w')
with open(INFILE, newline='', encoding='utf8', errors='replace') as f:
    reader = csv.reader(f, delimiter=',')
    try:
        for row in reader:
            if row[0] == '0' and negCount < LIMIT:
                negCount += 1
                outfile.write("\"{0}\",\"{1}\"\n".format(row[0], row[5]))
            elif row[0] == '4' and posCount < LIMIT:
                posCount += 1
                outfile.write("\"{0}\",\"{1}\"\n".format(row[0], row[5]))
    except UnicodeDecodeError as err:
        print('UnicodeDecodeError: {0}'.format(err))

outfile.close()

print('\nStats:')
print('{0} positive tags'.format(posCount))
print('{0} negative tags'.format(negCount))
print('\nTraining classifier')

# load up training data
feats = []
with open('trimmed.csv', newline='', encoding='utf8', errors='replace') as f:
    reader = csv.reader(f, delimiter=',')

    for row in reader:
        if (row[0] == '0'):
            feats.append((utils.word_feats(row[1]), 'neg'))
        elif (row[0] == '4'):
            feats.append((utils.word_feats(row[1]), 'pos'))

# delete trimmed dataset
os.remove('trimmed.csv')

# build classifier
classifier = NaiveBayesClassifier.train(feats)

utils.save_classifier(classifier)

print('Complete')
