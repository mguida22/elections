# _*_ coding:utf-8 _*_

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import tweepy
import pymongo
from httplib import IncompleteRead
from Config_Utils.config import config
from pykafka import KafkaClient
import json

CONSUMER_KEY = config.get_environment_variable('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = config.get_environment_variable('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN_KEY = config.get_environment_variable('TWITTER_ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = config.get_environment_variable(
    'TWITTER_ACCESS_TOKEN_SECRET')


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

client = KafkaClient(hosts='127.0.0.1:9092')
topic = client.topics[str('twitterfeed')]
producer = topic.get_producer(delivery_reports=False)

''' A kafka queue is created with a "topic" and the tweets are written on to that topic.
The storm topology is run and the spout reads off the tweets from the kafka queue
 and passes it to the bolt where further processing of the tweet can be done.
'''


class TweetExtractor(tweepy.StreamListener):

    def __init__(self, api, producer):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        self.Tweets = pymongo.MongoClient().tweets
        self.producer = producer

    def on_status(self, status):

        data = {}
        data['location'] = status.user.location
        data['text'] = status.text
        data['created_at'] = str(status.created_at)
        data['geo'] = status.geo
        candidate = self.identify_candidate_from_tweet(status.text)

        data['candidate'] = candidate
        print status.text
        # converting dictionary back to json format

        data['candidate'] = candidate

        json_tweet_format = json.dumps(data)

        # writing to Kafka Queue
        self.producer.produce(json_tweet_format)

    def identify_candidate_from_tweet(self, tweet):

        tweet_words = tweet.lower()

        if tweet_words.find("berniesanders") > 0 or tweet_words.find("bernie") > 0:
            return "berniesanders"
        if tweet_words.find("hillaryclinton") > 0 or tweet_words.find("hillary") > 0:
            return "hillaryclinton"
        if tweet_words.find("donaldtrump") > 0 or tweet_words.find("trump") > 0:
            return "donaldtrump"
        if tweet_words.find("tedcruz") > 0 or tweet_words.find("cruz") > 0:
            return "tedcruz"
        if tweet_words.find("johnkasich") > 0 or tweet_words.find("kasich") > 0:
            return "johnkasich"
        if tweet_words.find("marcorubio") > 0 or tweet_words.find("rubio") > 0:
            return "marcorubio"

        return "none"

    def save_tweets_to_db(self, data):
        self.Tweets.tweets.insert(data)

    # handle errors without closing stream:
    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True

try:
    sapi = tweepy.streaming.Stream(auth, TweetExtractor(api, producer))
    sapi.filter(track=['donaldtrump', 'donald trump', 'tedcruz', 'ted cruz',
                       'berniesanders',
                       'bernie sanders', 'hillaryclintion', 'hillary clintion',
                       'johnkasich', 'john kasich'])
except IncompleteRead:
    pass
