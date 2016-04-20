from pykafka import KafkaClient
import json


client = KafkaClient(hosts='127.0.0.1:9092')
sentiment_topic = client.topics[bytes('sentimentfeed', 'utf-8')]
sentiment_consumer = sentiment_topic.get_simple_consumer()

for message in sentiment_consumer:
    if message is not None:
        data = json.loads(message.value.decode('utf-8'))

        print('{0} - {1}'.format(data['sentiment'], data['candidate']))
