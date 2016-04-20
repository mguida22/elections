import datetime
import pymongo
import nltk
import matplotlib.pyplot as plt
from nltk.util import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from wordcloud import WordCloud
import numpy as np
from PIL import Image


def get_current_time():
    # getting current date
    current_time = datetime.datetime.now()
    # converting to the twitter date format
    current_time_twitter_format = current_time.strftime("%Y-%m-%d %H:%M:%S")
    # converting to a datetime object
    curr_time_datetime = datetime.datetime.strptime(
        current_time_twitter_format, '%Y-%m-%d %H:%M:%S')
    return curr_time_datetime


# to fetch tweets from mongo for the past m minutes pertaining to a
# particular candidate

def fetch_tweets_from_mongo(time_lapsed, candidate, user_time):

    tweet_list = []
    current_time = get_current_time()
    # print "current_time",current_time
    time_lapse = datetime.timedelta(minutes=time_lapsed)
    # print "time_lapse",time_lapse
    query_time = str(current_time - time_lapse)
    # print "query_time",query_time
    db = pymongo.MongoClient().tweets

    # TO-DO: rewrite query to include candidate name also
    cursor = db.newtesttweets.find({"created_at": {"$lt": query_time}})
    # print cursor.count()
    for document in cursor:
        tweet_list.append(document['text'])
    return tweet_list

# tokenize tweets and remove stopwords


def process_tweets(tweet_list):

    tweet_content = ' '.join(tweet_list)
    tweet_content = tweet_content.lower()

    # print len(tweet_content)
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(tweet_content)

    # tokens without any stop words
    filtered_tokens = []

    for word in tokens:
        if not word in custom_stop_words:
            filtered_tokens.append(word)

    return filtered_tokens

# to generate n-grams. can be used if unigrams dont make sense.


def generate_ngrams(tokens, ngram):

    bgs = ngrams(tokens, ngram)
    fdist = nltk.FreqDist(bgs)
    for k, v in fdist.items():
        if v > 5:
            print k[0], v

# currently using wordcloud library in python.


def generate_wordcloud(tokens):

    mask = np.array(Image.open("elections_image2.png"))
    token_string = " ".join(tokens)
    wordcloud = WordCloud(mask=mask, stopwords=custom_stop_words,
                          background_color='black', width=1800, height=1400).generate(token_string)
    print "generated wordcloud"
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.savefig('wordcloud_output.png', dpi=300)
    plt.show()

# add any other stop words that may not be in the nltk stopwords list.
custom_stop_words = set(stopwords.words("english"))
custom_stop_words.add('https')
custom_stop_words.add('rt')

tweet_list = fetch_tweets_from_mongo(60, "bernie", 0)
tokens = process_tweets(tweet_list)
generate_wordcloud(tokens)
