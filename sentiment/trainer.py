import csv
import random
import sys
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier

import utils


def train_classifier(feats_name):
    '''
    trains a classifier with given dataset and feature function
    '''
    # grab feats function
    feat_f = utils.feats[feats_name]

    # load up training data
    negfeats = []
    posfeats = []
    with open('trimmed.csv', newline='', encoding='utf8', errors='replace') as f:
        reader = csv.reader(f, delimiter=',')

        for row in reader:
            if (row[0] == '0'):
                negfeats.append((feat_f(row[1]), 'neg'))
            elif (row[0] == '4'):
                posfeats.append((feat_f(row[1]), 'pos'))

    # shuffle the data
    random.shuffle(negfeats)
    random.shuffle(posfeats)

    # percent cutoff for training and testing
    negcutoff = int(len(negfeats) * 0.75)
    poscutoff = int(len(posfeats) * 0.75)

    # divide dataset into training and testing
    trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
    testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]

    # build classifier
    classifier = NaiveBayesClassifier.train(trainfeats)

    # test classifier
    accuracy = nltk.classify.util.accuracy(classifier, testfeats)
    # print('\nAccuracy: '+ str(accuracy))
    # classifier.show_most_informative_features()

    return (classifier, accuracy)


def pick_classifier(classifiers, runs=1):
    '''
    Tests classifiers built from all datasets and feature functions.
    Will pick the best out of as many 'runs' are specified
    '''
    best = {
        'classifier': None,
        'accuracy': 0.0,
        'name': None
    }

    # test numerous classifiers, keep track of the most accurate
    for name in classifiers:
        # test runs number of classifiers from this dataset
        for i in range(0, runs):
            print('Training and testing \'{0}\' classifier. Run {1} of {2}'.format(
                name, i + 1, runs))
            # train the classifier with dataset and feature function
            curr_classifier, curr_accuracy = train_classifier(classifiers[name])

            print('Accuracy: {0}\n'.format(curr_accuracy))

            # store best
            if (curr_accuracy > best['accuracy']):
                best['accuracy'] = curr_accuracy
                best['classifier'] = curr_classifier
                best['name'] = name
                best['feats_name'] = classifiers[name]

    # save the best classifier by name
    print('Best classifier was \'{0}\' with an accuracy of {1}'.format(
        best['name'], best['accuracy']))

    return best

# specifiy dataset/feature functions here. There can be any combination of these
# format 'name': (dataset, feature_function, feature_function_name)
potential_classifiers = {
    'default_classifier': 'word_feats'
}

runs = 1
if len(sys.argv) == 2:
    runs = int(sys.argv[1])

classifier = pick_classifier(potential_classifiers, runs)

utils.save_classifier(classifier['name'], classifier[
                      'classifier'], classifier['feats_name'])
