import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
import plotly.graph_objs as graph
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

app = dash.Dash()
app.config.supress_callback_exceptions=True

my_css_url = "https://codepen.io/TeeOhh/pen/XEJRBb.css"

app.css.append_css({
	"external_url": my_css_url
})

app.layout = html.Div([
	html.Div([
		html.P('Twitter Classifier. Author: Taylor Olson', style={'margin-bottom': '5%'})
		], id='header'),
	html.Div([
        dcc.Input(id='tweet_amount', type='number', value='50'),
		html.Button('Load Tweets', id='load-btn', style={'margin-bottom': '10%'}),
		html.Div(['Load tweets and after they will be shown here...'], id="twitter_feed")
	])
	], id="main-content")

def generate_table(dataframe, max_rows):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in ['user', 'tweet_text', 'label']])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in ['user', 'tweet_text', 'label']
        ]) for i in range(min(len(dataframe), max_rows))]
    )	

@app.callback(
    Output('twitter_feed', 'children'),
    events = [Event('load-btn', 'click')],
    state = [State('tweet_amount', 'value')])

def load_table(amount):
	past_tweets_df = pd.read_csv('past_tweets.csv', usecols = ['user', 'location','tweet_text', 'label'])
	past_tweets_df = past_tweets_df.tail(int(amount)).iloc[::-1]
	return generate_table(past_tweets_df, int(amount))

if __name__ == '__main__':
	app.run_server(debug=True)