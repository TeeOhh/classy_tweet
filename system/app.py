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
		html.P('SVM Abortion Tweet Classifier'),
		html.P('Author: Taylor Olson', style={'margin-bottom': '5%'}),
		], id='header'),
	html.Div([
		dcc.Input(id='tweet_amount', type='number', value='50'),
		html.Button('Load Tweets', id='load-btn', style={'margin-bottom': '3%'}),
		dcc.RadioItems(
			options=[
				{'label': 'Table View', 'value': 'table'},
				{'label': 'Map View', 'value': 'map'}
			],
			value='table',
			id='table_or_map',
			style={'margin-bottom': '5%'}
		),
		html.Div(['Load tweets and after they will be shown here...'], id="twitter_feed"),
	], id="content")
	], id="main-content")

def generate_table(df, max_rows):
	df_for = df[(df['label'] == 'for')]
	df_against = df[(df['label'] == 'against')]
	df_neutral = df[(df['label'] == 'neutral')]
	return html.Table(
		# Header
		[html.Tr([html.Th(col) for col in ['User', 'Tweet']])] +

		# Body
		[html.Tr([
			html.Td(df_for.iloc[i][col]) for col in ['user', 'tweet_text']
		], style={'border' : '3px solid #00b300'}) for i in range(min(len(df_for), max_rows))] +

		[html.Tr([
			html.Td(df_against.iloc[i][col]) for col in ['user', 'tweet_text']
		], style={'border' : '3px solid #ff4d4d'}) for i in range(min(len(df_against), max_rows))] +

		[html.Tr([
			html.Td(df_neutral.iloc[i][col]) for col in ['user', 'tweet_text']
		], style={'border' : '3px solid #595959'}) for i in range(min(len(df_neutral), max_rows))]
	)

def generate_map(df):
	df_for = df[(df['label'] == 'for')]
	df_against = df[(df['label'] == 'against')]
	df_neutral = df[(df['label'] == 'neutral')]
	data = [ dict(
			type = 'scattergeo',
			name = 'Pro Abortion',
			locationmode = 'USA-states',
			lon = df_for['long'],
			lat = df_for['lat'],
			text = df_for['tweet_text'],
			mode= 'markers',
			hoverinfo = 'text',
			marker = dict(
				size = 5,
				opacity = 0.8,
				symbol = 'circle',
				color = 'rgb(0, 128, 0)'
				)
		),
		dict(
			type = 'scattergeo',
			name = 'Against Abortion',
			locationmode = 'USA-states',
			lon = df_against['long'],
			lat = df_against['lat'],
			text = df_against['tweet_text'],
			mode= 'markers',
			hoverinfo = 'text',
			marker = dict(
				size = 5,
				opacity = 0.8,
				symbol = 'circle',
				color = 'rgb(255, 0, 0)'
				)
		),
		dict(
			type = 'scattergeo',
			name = 'Neutral',
			locationmode = 'USA-states',
			lon = df_neutral['long'],
			lat = df_neutral['lat'],
			text = df_neutral['tweet_text'],
			mode= 'markers',
			hoverinfo = 'text',
			marker = dict(
				size = 5,
				opacity = 0.8,
				symbol = 'circle',
				color = 'rgb(128, 128, 128)'
				)
		)]
	layout = dict(
		title = 'U.S. Tweets on Abortion',
		colorbar = True,
		geo = dict(
			scope='usa',
			projection=dict( type='albers usa' ),
			showland = True,
			landcolor = "rgb(250, 250, 250)",
			subunitcolor = "rgb(77, 77, 77)",
			countrycolor = "rgb(77, 77, 77)",
			countrywidth = 0.5,
			subunitwidth = 0.5,
		),
	)
	fig = dict(data=data, layout=layout)
	return dcc.Graph(id='graph', figure=fig)  

@app.callback(
	Output('twitter_feed', 'children'),
	events = [Event('load-btn', 'click')],
	state = [State('tweet_amount', 'value'), State('table_or_map', 'value')])

def load_content(amount, table_map):
	past_tweets_df = pd.read_csv('past_tweets.csv', usecols = ['user', 
		'location', 'lat', 'long', 'tweet_text', 'label'])

	if table_map == 'table':
		past_tweets_df = past_tweets_df.tail(int(amount)).iloc[::-1]
		return generate_table(past_tweets_df, int(amount))

	elif table_map == 'map':
		past_tweets_df = past_tweets_df[(past_tweets_df['lat'] != 0) & (past_tweets_df['long'] != 0)]
		past_tweets_df = past_tweets_df.tail(int(amount)).iloc[::-1]
		return generate_map(past_tweets_df)

if __name__ == '__main__':
	app.run_server(debug=True)