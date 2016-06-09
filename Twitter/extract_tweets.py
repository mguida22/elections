# _*_ coding:utf-8 _*_

import sys
import tweepy
import json


class TweetExtractor(tweepy.StreamListener):

    def __init__(self, api, producer):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        self.producer = producer

    def on_status(self, status):
        data = {}
        # data['location'] = status.user.location
        data['text'] = status.text
        # data['created_at'] = str(status.created_at)
        # data['geo'] = status.geo
        candidate = self.identify_candidate_from_tweet(status.text)
        data["candidate"] = candidate

        if candidate != None:

            # converting dictionary back to json format
            json_tweet_format = json.dumps(data)

            # writing to Kafka Queue
            self.producer.produce(bytes(json_tweet_format, 'utf-8'))

    def identify_candidate_from_tweet(self, tweet):

        tweet_words = tweet.lower()

        if tweet_words.find("sanders") > 0 or tweet_words.find("bernie") > 0:
            return "berniesanders"
        if tweet_words.find("clinton") > 0 or tweet_words.find("hillary") > 0:
            return "hillaryclinton"
        if tweet_words.find("donald") > 0 or tweet_words.find("trump") > 0:
            return "donaldtrump"

        return None

    # handle errors without closing stream:
    def on_error(self, status_code):
        print('Encountered error with status code: {0}'.format(
            status_code), file=sys.stderr)
        return True

    def on_timeout(self):
        print('Timeout...', file=sys.stderr)
        return True
