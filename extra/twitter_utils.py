##Functions used for tweet pulling
import tweepy
from tweepy import OAuthHandler
import pandas as pd
import time

##tweepy docs: http://tweepy.readthedocs.io/en/v3.5.0/
##twitter JSON objects: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/intro-to-tweet-json

## ----- Set up twitter connection -----

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

def get_issue_tweets(issue):
	##Function retrives max amount of tweets containing the corresponding ethical issue hashtag
	##Params: ethical issue hashtag (string)
	##Returns: list of tweets (strings)

	for tweet in tweepy.Cursor(api.search, q=issue, lang='en').items():
		##only add tweet to list if it's not a retweet and doesn't contain links
		if ('https' not in tweet.text) and ('RT @' not in tweet.text):
			##build dataframe with columns: tweet text, location, date
			df = pd.DataFrame([{'location' : tweet.user.location, 'label': '', 'tweet_text' : tweet.text}])
			while ' ' in issue:
				issue = issue.replace(' ', '_')
			with open(str(issue) + '_data.csv', 'a+') as f:
				df.to_csv(f, header=False)