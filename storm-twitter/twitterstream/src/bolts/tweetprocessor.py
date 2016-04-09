from __future__ import absolute_import, print_function, unicode_literals

from collections import Counter
from streamparse.bolt import Bolt


class TweetProcessor(Bolt):

    def initialize(self, conf, ctx):
    	#print "Ready to process tweets"
        self.counts = Counter()

    def process(self, tup):
        word = tup.values[0]
        #self.counts[word] += 1
        self.emit([word])
        self.log('%s' % (word))
