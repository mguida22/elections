# consumer


from streamparse.spout import Spout
from pykafka import KafkaClient

# This spout reads off tweets from the Kafka Queue.


class TweetSpout(Spout):
    words = []

    def initialize(self, stormconf, context):

        # create a kafka client
        client = KafkaClient(hosts='127.0.0.1:9092')

        # look into the topic "tweets" where the producer pushes the tweets.
        self.topic = client.topics[str('twitterfeed')]

    def next_tuple(self):
        consumer = self.topic.get_simple_consumer()
        for message in consumer:
            if message is not None:
                self.emit([message.value])
        else:
            self.emit()
