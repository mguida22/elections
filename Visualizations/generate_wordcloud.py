#!/usr/bin/env python
import datetime
import pymongo
import nltk
from nltk.util import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from wordcloud import WordCloud
import numpy as np
from PIL import Image
import sys


def get_current_time():
    # getting current date
    current_time = datetime.datetime.now()
    # converting to the twitter date format
    current_time_twitter_format = current_time.strftime("%Y-%m-%d %H:%M:%S")
    # converting to a datetime object
    curr_time_datetime = datetime.datetime.strptime(
        current_time_twitter_format, '%Y-%m-%d %H:%M:%S')
    return curr_time_datetime

# to fetch tweets from mongo for the past m minutes pertaining to a particular candidate
def fetch_tweets_from_mongo(time_lapsed, candidate):

	tweet_list = []
	current_time = get_current_time()
	print "current_time",current_time
	time_lapse = datetime.timedelta(minutes=time_lapsed)
	#print "time_lapse",time_lapse
	query_time = current_time - time_lapse
	print "query_time",query_time
	db = pymongo.MongoClient().tweets

	#TO-DO: rewrite query to include candidate name also
	cursor = db.latest_tweets.find({ "$and": [ {"created_at":{ "$gt": query_time}}, { "candidate": candidate} ] })
	
	# for displaying stats about the number of tweets
	tweet_count = cursor.count()
	print tweet_count
	
	for document in cursor:
		tweet_list.append(document['text'])
	return tweet_list


def process_tweets(tweet_list):

	tweet_content = ' '.join(tweet_list)
	tweet_content = tweet_content.lower()
	
	#print len(tweet_content)
	tokenizer = RegexpTokenizer(r'\w+')
	tokens = tokenizer.tokenize(tweet_content)
	
	#tokens without any stop words
	filtered_tokens = [] 

	for word in tokens:
		if not word in custom_stop_words:
			filtered_tokens.append(word)
	
	#print "tweets processed"
    #filtered_tokens = filtered_tokens[:100]
	return filtered_tokens

#currently using wordcloud library in python.
def generate_wordcloud(tokens, candidate,filepath):

	mask = np.array(Image.open(filepath))
	token_string = " ".join(tokens)
	wordcloud = WordCloud(mask=mask,stopwords=custom_stop_words,background_color='black',width=1800,height=1400).generate(token_string)
	image = wordcloud.to_image()
	image.save('/Users/narainsharma/Desktop/BigData/Elections/Visualizations/'+candidate+'.png')
	#print image
	image.show()
	#plt.show()


mask_filepath = "/Users/narainsharma/Desktop/BigData/Elections/Visualizations/elections_image2.png"


# add any other stop words that may not be in the nltk stopwords list.
custom_stop_words = set(stopwords.words("english"))
custom_stop_words.add('https')
custom_stop_words.add('rt')

trump_tweets = fetch_tweets_from_mongo(1, "donaldtrump")
sanders_tweets = fetch_tweets_from_mongo(1,"berniesanders")
clinton_tweets = fetch_tweets_from_mongo(1,"hillaryclinton")
cruz_tweets  = fetch_tweets_from_mongo(1,"tedcruz")
kasich_tweets = fetch_tweets_from_mongo(1,"johnkasich")

trump_tokens = process_tweets(trump_tweets)
sanders_tokens = process_tweets(sanders_tweets)
clinton_tokens = process_tweets(clinton_tweets)
cruz_tokens = process_tweets(cruz_tweets)
kasich_tokens = process_tweets(kasich_tweets)

generate_wordcloud(trump_tokens,"trump",mask_filepath)
generate_wordcloud(sanders_tokens,"sanders",mask_filepath)
generate_wordcloud(clinton_tokens,"clinton",mask_filepath)
generate_wordcloud(cruz_tokens,"crux",mask_filepath)
generate_wordcloud(kasich_tokens,"kasich",mask_filepath)