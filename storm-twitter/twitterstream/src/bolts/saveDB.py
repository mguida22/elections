from __future__ import absolute_import, print_function, unicode_literals
from datetime import datetime
from collections import Counter
from streamparse.bolt import Bolt
import pymongo
import json


class DatabaseBolt(Bolt):

    def initialize(self, conf, ctx):
        # print "Ready to process tweets"
        self.counts = Counter()
        self.db = pymongo.MongoClient().tweets

    def process(self, tup):
        #location = tup.values[0]
        json_tweet = tup.values[0]
        data = json.loads(json_tweet)

        tweet_created_at = data['created_at']

        self.db.newtesttweets.insert(data)
        # self.emit([tweet_text.encode('ascii','ignore')])

        # for checking if this is working.
        self.log('%s' % (tweet_created_at.encode('ascii', 'ignore')))
