from __future__ import absolute_import, print_function, unicode_literals

from collections import Counter
from streamparse.bolt import Bolt
import pymongo
import json

class DatabaseBolt(Bolt):

    def initialize(self, conf, ctx):
    	#print "Ready to process tweets"
        self.counts = Counter()
        self.test = pymongo.MongoClient().testtweets


    def process(self, tup):
        #location = tup.values[0]
        json_tweet = tup.values[0]

        

        data = json.loads(json_tweet)
        tweet_text = data['text']
        tweet_created_at = data['created_at']
        
        self.emit([tweet_text.encode('ascii','ignore')])
        #self.log('%s' % (location))
        self.log('%s' % (tweet_created_at.encode('ascii','ignore')))

