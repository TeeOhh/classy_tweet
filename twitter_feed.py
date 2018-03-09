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
			time.sleep(15 * 60)
			continue
		except KeyboardInterrupt:
			break

def get_issue_tweets():
	##Function retrives max amount of tweets containing the corresponding ethical issue hashtag
	##Params: ethical issue hashtag (string)
	##Returns: list of tweets (strings)

	##Print out past saved tweets onto timeline
	# past_tweets_df = pd.read_csv('past_tweets.csv', usecols = ['user', 'location','tweet_text', 'label'])
	# past_tweets_df = past_tweets_df.tail(50)
	# past_tweets_df.columns = ['user', 'location','tweet_text', 'label']
	# with open('past_tweets.csv', 'w') as f:
	# 			past_tweets_df.to_csv(f, index=False)
	# print(past_tweets_df)
	# print('-' * 50)



	##Load classifier
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
			tweet_text = tweet.text
			tweet_class = classifier.predict([utils.clean_single_tweet(tweet_text)])[0]
			columns = ['user', 'location','tweet_text', 'label']
			df = pd.DataFrame([{'user' : user, 'location' : location,
				'tweet_text' : tweet_text, 'label': tweet_class}])
			df = df[columns]
			print("%s  |  %s  |  %s |  %s" % (user, location, tweet_text, tweet_class))
			# with open('past_tweets.csv', 'a+') as f:
			# 	df.to_csv(f, header=False, index=False)
			print('-' * 50)
			time.sleep(3)
			
get_issue_tweets()