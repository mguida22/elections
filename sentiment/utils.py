import pickle


def save_classifier(classifier, name):
    '''
    save the given classifier by name
    '''
    if not name.endswith('.pickle'):
        name = name + '.pickle'

    f = open(name, 'wb')
    pickle.dump(classifier, f)
    f.close()

    print('Saved classifier to {0}'.format(name))


def load_classifier(file_path):
    '''
    load the classifier by file path
    '''
    f = open(file_path, 'rb')
    classifier = pickle.load(f)
    f.close()

    return classifier
