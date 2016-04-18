# _*_ coding:utf-8 _*_
import tweepy
import sys
import  pymongo
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

''' A kafka queue is created with a "topic" and the tweets are written on to that topic.
The storm topology is run and the spout reads off the tweets from the kafka queue
 and passes it to the bolt where further processing of the tweet can be done.
'''
class TweetExtractor(tweepy.StreamListener):

    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        self.Tweets = pymongo.MongoClient().tweets

    def on_status(self, status):
        
        data = {}
        data['location'] = status.user.location
        data['text'] = status.text
        data['created_at'] = str(status.created_at)
        data['geo'] = status.geo
       
        #converting dictionary back to json format       
        json_tweet_format = json.dumps(data)
        #print json_tweet_format, type(json_tweet_format)

        #saving to MongoDB; comment out if not needed
        #self.save_tweets_to_db(data)

        #writing to Kafka Queue
        client = KafkaClient(hosts='127.0.0.1:9092')
        topic = client.topics[str('testtweets7')]
        with topic.get_producer(delivery_reports=False) as producer:
            #tweet = status.text.encode('ascii','ignore')
            
            #if status.user.location is None:
                #location = status.user.location
            #else:
                #location = status.user.location.encode('ascii','ignore')
            #created_at = str(status.created_at)
            #geo = str(status.geo)
            print json_tweet_format
            #print location
            #print created_at
            #print geo
            #if location is None:
                #producer.produce("NONE " + tweet)
            #else:
                #producer.produce(location + tweet)
            producer.produce(json_tweet_format)
            #producer.produce(created_at)
            #producer.produce(geo)
            

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