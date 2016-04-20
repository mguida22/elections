from Config_Utils.config import config
from sentiment.analyzer import Analyzer

from pykafka import KafkaClient
import json


client = KafkaClient(hosts='127.0.0.1:9092')
tweet_topic = client.topics[bytes('twitterfeed', 'utf-8')]
sentiment_topic = client.topics[bytes('sentimentfeed', 'utf-8')]
sentiment_producer = sentiment_topic.get_producer(delivery_reports=False)
tweet_consumer = tweet_topic.get_simple_consumer()

analyzer = Analyzer()


for message in tweet_consumer:
    if message is not None:
        tweet_data = json.loads(message.value.decode('utf-8'))

        data = {}
        data['candidate'] = tweet_data['candidate']
        data['sentiment'] = analyzer.classify(tweet_data['text'])

        json_tweet_format = json.dumps(data)

        sentiment_producer.produce(bytes(json_tweet_format, 'utf-8'))
