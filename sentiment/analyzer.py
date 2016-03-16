#!/usr/bin/env python3

import os

import utils


class Analyzer:

    def __init__(self, classifier='default_classifier'):
        self.classifier, self.feats = utils.load_classifier(classifier)

    def classify(self, s):
        return self.classifier.classify(self.feats, s)
