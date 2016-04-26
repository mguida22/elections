from __future__ import absolute_import, print_function, unicode_literals

from collections import Counter
from streamparse.bolt import Bolt
import json

class TweetProcessor(Bolt):

    def initialize(self, conf, ctx):
    	#print "Ready to process tweets"
        self.counts = Counter()

    def process(self, tup):
    	#location = tup.values[0]
        json_tweet = tup.values[0]
        dict_tweet = json.loads(json_tweet)


        tweet_text = dict_tweet['text']

        # The tweet_text is available. Use this to perform sentiment analysis.

        #self.emit([tweet_text])
        
        #for checking if this is working.
        self.log('%s' % (tweet_text.encode('ascii','ignore')))
