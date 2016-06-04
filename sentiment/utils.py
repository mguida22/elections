import pickle
import os.path
import re


STOPWORDS = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
             'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
             'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
             'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
             'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
             'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but',
             'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
             'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
             'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
             'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
             'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
             'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
             'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']


def save_classifier(classifier):
    '''
    save the given classifier
    '''

    name = 'default_classifier.pickle'
    with open(name, 'wb') as f:
        pickle.dump(classifier, f)
        print('Saved classifier to {0}'.format(name))


def load_classifier(path):
    '''
    load the classifier by file path
    '''
    if os.path.isfile(path) is False:
        raise FileNotFoundError(path)

    with open(path, 'rb') as f:
        return pickle.load(f)


def word_feats(words):
    '''
    create dictionary of features
    '''
    d = {}
    words = words.split(' ')
    for word in words:
        word = word.lower()
        word = re.sub('[^a-zA-Z#@]+', '', word)
        if len(word) is not 0:
            if word not in STOPWORDS:
                d[word] = True
            else:
                d[word] = False

    return d
