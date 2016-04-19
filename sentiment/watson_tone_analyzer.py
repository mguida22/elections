# -*- coding: utf-8 -*-
import json
from watson_developer_cloud import ToneAnalyzerV3Beta as ToneAnalyzer
import  pymongo

from Config_Utils.config import config

WATSON_KEY = config.get_environment_variable('WATSON_KEY')
WATSON_PASSWORD = config.get_environment_variable('WATSON_PASSWORD')

#create Bluemix account to get service_username and service_password
tone_analyzer = ToneAnalyzer(username=WATSON_KEY,
                             password=WATSON_PASSWORD,
                             version='2016-02-11')

def get_tweets_from_db():
	db = pymongo.MongoClient().tweets
	cursor = db.tweets.find({})
	return cursor

def get_sentiment_from_watson(cursor):

	#selecting 100 tweets
	cursor = cursor[:100]
	for document in cursor:
		tweet = document['text']
		sentimentData = tone_analyzer.tone(text=tweet)
		anger=sentimentData["document_tone"]["tone_categories"][0]["tones"][0]["score"]
		disgust=sentimentData["document_tone"]["tone_categories"][0]["tones"][1]["score"]
		joy=sentimentData["document_tone"]["tone_categories"][0]["tones"][3]["score"]
		sadness = sentimentData["document_tone"]["tone_categories"][0]["tones"][4]["score"]
		openness = sentimentData["document_tone"]["tone_categories"][2]["tones"][0]["score"]
		extraversion = sentimentData["document_tone"]["tone_categories"][2]["tones"][2]["score"]
		aggreablesness = sentimentData["document_tone"]["tone_categories"][2]["tones"][3]["score"]
		neuroticism=sentimentData["document_tone"]["tone_categories"][2]["tones"][4]["score"]
		print tweet,anger,disgust,joy,sadness,openness,extraversion,aggreablesness,neuroticism


tweets = get_tweets_from_db()
get_sentiment_from_watson(tweets)