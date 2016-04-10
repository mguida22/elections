from __future__ import absolute_import, print_function, unicode_literals

from collections import Counter
from streamparse.bolt import Bolt
import pymongo

class DatabaseBolt(Bolt):

    def initialize(self, conf, ctx):
    	#print "Ready to process tweets"
        self.counts = Counter()
        self.test = pymongo.MongoClient().testtweets


    def process(self, tup):
        word = tup.values[0]
        #self.counts[word] += 1
        data = {}
        data['text'] = word

        self.emit([word])
        self.log('%s' % (word))
        self.test.testtweets.insert(data)
