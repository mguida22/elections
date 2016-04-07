#!/usr/bin/env python3

from analyzer import Analyzer

a = Analyzer()

while True:
    print(a.classify(input('? ')))
