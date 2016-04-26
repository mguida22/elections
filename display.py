from pykafka import KafkaClient
import json
import sys

if len(sys.argv) < 2:
    print("please enter a command line argument for the stream you want to read")
    print("example: python display.py sentimentfeed")
    exit()


client = KafkaClient(hosts='127.0.0.1:9092')
sentiment_topic = client.topics[bytes(sys.argv[1], 'utf-8')]
sentiment_consumer = sentiment_topic.get_simple_consumer()

for message in sentiment_consumer:
    if message is not None:
        data = json.loads(message.value.decode('utf-8'))

        print('{0} - {1}'.format(data['sentiment'], data['candidate']))
