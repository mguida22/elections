#!/usr/bin/env python3

from sentiment.analyzer import Analyzer

a = Analyzer('sentiment/default_classifier.pickle')

while True:
    print(a.classify(input('? ')))
