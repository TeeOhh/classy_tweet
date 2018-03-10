##Removes duplicate tweets after pulling
import pandas as pd

df = pd.read_csv('past_tweets.csv')
df = df.drop_duplicates(subset='tweet_text', keep='first')
df.to_csv('past_tweets.csv', columns=['user', 'location', 'tweet_text', 'label'])
