from Config_Utils.config import config
from Twitter.extract_tweets import TweetExtractor

from pykafka import KafkaClient
import tweepy
from http.client import IncompleteRead
import json
from datetime import datetime


CONSUMER_KEY = config.get_environment_variable('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = config.get_environment_variable('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN_KEY = config.get_environment_variable('TWITTER_ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = config.get_environment_variable(
    'TWITTER_ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

''' A kafka queue is created with a "topic" and the tweets are written on to that topic.
The storm topology is run and the spout reads off the tweets from the kafka queue
 and passes it to the bolt where further processing of the tweet can be done.
'''
client = KafkaClient(hosts='127.0.0.1:9092')
tweet_topic = client.topics[bytes('twitterfeed', 'utf-8')]
tweet_producer = tweet_topic.get_producer(delivery_reports=False,
                                          linger_ms=500)

while True:
    try:
        sapi = tweepy.streaming.Stream(
            auth, TweetExtractor(api, tweet_producer))
        sapi.filter(track=['donaldtrump', 'donald trump',
                           'hillaryclintion', 'hillary clintion'])
    except IncompleteRead:
        pass
    except AttributeError:
        # Tweepy has doens't handle this on their own.
        # https://github.com/tweepy/tweepy/issues/576
        print('[{0}] AttributeError: Retrying the streaming connection.'.format(str(datetime.now())))
        continue
    except TypeError:
        # Tweepy also doesn't handle this...
        # https://github.com/tweepy/tweepy/issues/674
        print('[{0}] TypeError: Retrying the streaming connection.'.format(str(datetime.now())))
        continue
    break
