#!/usr/bin/env python3

import os

from .utils import load_classifier


class Analyzer:

    def __init__(self, classifier='default_classifier'):
        self.classifier, self.feats = load_classifier(classifier)

    def classify(self, s):
        tokenized = self.feats(s)
        return self.classifier.classify(tokenized)
