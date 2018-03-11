import tweepy
from tweepy import OAuthHandler
import pandas as pd
import time
import pickle
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
import cleaning_utils as utils
from sklearn import svm

## ----------- Load keys for tweepy -----------------

keys_file = open('/home/taylor/coding/twitter_config', 'r')
x = 0
for line in keys_file:
	line = line.strip()
	if x==0:
		consumer_key = line
	elif x==1:
		consumer_secret = line
	elif x==2:
		access_token = line
	elif x==3:
		access_secret = line
	x += 1
keys_file.close()
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

def limit_handled(cursor):
	while True:
		try:
			yield cursor.next()
		except tweepy.RateLimitError:
			time.sleep(15*60)
			return
		except KeyboardInterrupt:
			break

def load_tweets():
	file = open('svm_classy.p', 'rb')
	classifier = pickle.load(file)
	file.close()

	for tweet in tweepy.Cursor(api.search, q='abortion', lang='en').items():
		##only add tweet to list if it's not a retweet and doesn't contain links
		if ('https' not in tweet.text) and ('RT @' not in tweet.text):
			##build dataframe with columns: tweet text, location, date
			##JSON Object: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/intro-to-tweet-json
			user = tweet.user.screen_name
			location = tweet.user.location
			geo_location = utils.geo_location(location)
			if geo_location != '':
				latitude = geo_location[0]
				longitude = geo_location[1]
			else:
				latitude = 0
				longitude = 0
			tweet_text = tweet.text
			tweet_class = classifier.predict([utils.clean_single_tweet(tweet_text)])[0]
			columns = ['user', 'location', 'lat', 'long', 'tweet_text', 'label']
			df = pd.DataFrame([{'user' : user, 'location' : location,
				'lat': latitude, 'long' : longitude, 'tweet_text' : tweet_text, 
				'label': tweet_class}])
			df = df[columns]
			
			with open('past_tweets.csv', 'a+') as f:
				df.to_csv(f, header=False, index=False)

load_tweets()