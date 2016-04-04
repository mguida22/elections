import tweepy
import sys
import pymongo
from httplib import IncompleteRead
from Config_Utils.config import config

CONSUMER_KEY = config.get_environment_variable('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = config.get_environment_variable('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN_KEY = config.get_environment_variable('TWITTER_ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = config.get_environment_variable(
    'TWITTER_ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


class TweetExtractor(tweepy.StreamListener):

    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        self.Tweets = pymongo.MongoClient().tweets

    def on_status(self, status):
        # print status.text, "\n"

        data = {}

        data['location'] = status.user.location
        data['text'] = status.text
        data['created_at'] = status.created_at
        data['geo'] = status.geo
        self.save_tweets_to_db(data)

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
    sapi = tweepy.streaming.Stream(auth, TweetExtractor(api))
    sapi.filter(track=['donaldtrump', 'donald trump', 'tedcruz', 'ted cruz',
                       'marcorubio', 'marco rubio', 'berniesanders',
                       'bernie sanders', 'hillaryclintion', 'hillary clintion',
                       'johnkasich', 'john kasich'])
except IncompleteRead:
    pass
