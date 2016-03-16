import pickle
import os.path
import json


def save_classifier(name, classifier, feats_name):
    '''
    save the given classifier by name
    '''
    if os.path.isfile('config.json') is True:
        with open('config.json', 'r') as f:
            try:
                config = json.load(f)
            except:
                config = {}
    else:
        config = {}

    config[name] = {}
    config[name]['classifier_path'] = name + '.pickle'
    config[name]['feats_name'] = feats_name

    with open('config.json', 'w') as f:
        print(json.dumps(config, indent=4), file=f)

    name = name + '.pickle'
    with open(name, 'wb') as f:
        pickle.dump(classifier, f)
        print('Saved classifier to {0}'.format(name))


def load_classifier(name):
    '''
    load the classifier by file path
    '''
    if os.path.isfile('config.json') is True:
        with open('config.json', 'r') as f:
            try:
                config = json.load(f)
            except:
                print('Check config.json')
                raise
    else:
        raise FileNotFoundError('config.json')

    with open(config[name]['classifier_path'], 'rb') as f:
        return (pickle.load(f), feats[config[name]['feats_name']])


def word_feats(words):
    '''
    create dictionary of features, all words are True for now
    '''
    return dict([(word, True) for word in words])

feats = {
    'word_feats': word_feats
}
