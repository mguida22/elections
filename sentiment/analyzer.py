#!/usr/bin/env python3

import os

from .utils import load_classifier, word_feats


class Analyzer:

    def __init__(self, classifier='default_classifier.pickle'):
        self.classifier = load_classifier(classifier)

    def classify(self, s):
        tokenized = word_feats(s)
        return self.classifier.classify(tokenized)
