import re
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import gensim
from gensim import corpora, models, similarities
import pandas as pd

def clean_single_tweet(tweet):
	tweet = remove_handles(tweet)
	tweet = remove_non_english(tweet)
	tweet = remove_numbers(tweet)
	tweet = tweet.lower()
	tweet = remove_punc(tweet)
	tweet = remove_stop(tweet)
	tweet = remove_double_space(tweet)
	tweet = plural_hashtag(tweet, "abortion")
	tweet = tweet.replace("abortion", "")
	tweet = remove_double_space(tweet)
	return tweet


def remove_handles(tweet):
    ##Function takes in a string (a tweet) and returns the string without twitter handles
    tweet = str(tweet).split(' ')
    filtered_words = [word for word in tweet if '@' not in word]
    return ' '.join(filtered_words)


def remove_non_english(tweet):
    ##Function takes in a tweet and returns the tweet with non-english (including emojis) removed
    stripped = [str(c ) for c in tweet if 0 < ord(c) < 127]
    return ''.join(stripped)

##ASCII TABLE: http://www.asciitable.com/
def remove_numbers(tweet):
    ##Takes in a tweet and returns the tweet with all of the numbers removed
    text = str(tweet)
    match = re.compile('\d')
    return re.sub(match, '', tweet)

def remove_punc(tweet):
    ##Takes in a tweet and removes the desired punctuation defined in the remove list
    remove=['.', ',', '!', '?', ':', ';', '$', '%', '&amp', '&', '*', '(', ')', '+', '=', '<', '>', 
            '/', '\\', '~', '"', '|', '{', '}', '[', ']']
    for punc in remove:
        tweet = tweet.replace(punc, '')
    return tweet

def remove_stop(tweet):
    words = tweet.split(" ")
    # stop_words=[word for word in stopwords.words('english')]
    # stop_words.remove('why')
    # stop_words.remove('not')
    # stop_words.remove('how')
    # stop_words.remove('for')
    # stop_words.remove('having')
    # stop_words.remove('against')
    # stop_words.remove('before')
    # stop_words.remove('after')
    # stop_words.remove('when')
    # stop_words.remove('own')
    # stop_words.remove('should')
    # stop_words.remove('will')
    # stop_words.remove('just')
    stop_words = ['a', 'the']
    filtered_words = [word for word in words if not word.lower() in stop_words]
    return " ".join(filtered_words)

def remove_double_space(tweet):
    ##Takes in a tweet adds spaces before hashtags, then replaces occurences of 2,3,4,5 spaces with a single one
    tweet = tweet.replace('#', ' #')
    tweet = tweet.strip()
    while '\n' in tweet:
        tweet = tweet.replace('\n', ' ')
    for x in range(2, 10):
        space = " " * x
        while space in tweet:
            tweet = tweet.replace(space, " ")
    return tweet

def plural_hashtag(tweet, issue):
	tweet = tweet.replace(" #" + issue + " ", " " + issue + " ")
	tweet = tweet.replace(" #" + issue, " " + issue)
	tweet = tweet.replace("#" + issue + " ", issue + " ")
	tweet = tweet.replace("#" + issue, issue)
	tweet = tweet.replace(" " + issue + "s ", " " + issue + " ")
	tweet = tweet.replace(" " + issue + "s", " " + issue)
	tweet = tweet.replace(issue + "s ", issue + " ")
	tweet = tweet.replace(issue + "s", issue)
	return tweet

def build_freq_matrix(data_frame):
    ##Takes in the data from of dates, location, tweet text
    ##and returns a dataframe of words as columns, indexed by tweet text
    ##as rows. Each entry is the frequency of the word in that tweet.
    columns = data_frame.columns.values.tolist()
    tweets = data_frame.iloc[:, columns.index('tweet_text')].tolist()
    tweet_texts = tweets
    tweets = [tweet.strip().split(" ") for tweet in tweets]
    dictionary = gensim.corpora.Dictionary(tweets)
    corpus = [dictionary.doc2bow(tweet) for tweet in tweets]
    numpy_array = gensim.matutils.corpus2dense(corpus, num_terms=len(dictionary))
    term_freq = pd.DataFrame(numpy_array).T
    words = [word for word, id in dictionary.token2id.items()]
    term_freq.columns = words
    term_freq['tweet_text'] = tweet_texts
    term_freq = term_freq.set_index('tweet_text')
    return term_freq

def make_binary(integer):
    if integer > 0:
        return 1
    else:
        return 0
    
def remove_words(tweet, words):
    ##Remove words from the tweet texts if their not within the thresholds
    tweet = tweet.split(" ")
    for word in tweet:
        if word not in words:
            while word in tweet:
                tweet.remove(word)
    return " ".join(tweet)
    
def remove_thresholds(dataframe, freq_matrix, lower_thresh, upper_thresh):
    ## Takes in the dataframe with date, location, and tweet text columns, a lower thresh decimal, a upper thresh decimal
    ## Then returns a new dataframe with the words that occur outside threshold * total tweets of upper and lower removed
    ## as well as the words below the lower threshold and above the upper threshold
    
    binary_matrix = freq_matrix.applymap(make_binary)
    sum_matrix = binary_matrix.apply(sum).to_frame()
    lower_cutoff = round(lower_thresh * len(freq_matrix))
    upper_cutoff = round(upper_thresh * len(freq_matrix))
    lower_matrix = sum_matrix.loc[sum_matrix[0] < lower_cutoff]
    upper_matrix = sum_matrix.loc[sum_matrix[0] > upper_cutoff]
    sum_matrix = sum_matrix.loc[sum_matrix[0] <= upper_cutoff]
    sum_matrix = sum_matrix.loc[sum_matrix[0] >= lower_cutoff]
    keep_words = sum_matrix.index
    df_copy = dataframe.copy()
    df_copy['tweet_text'] = dataframe.apply(lambda x: remove_words(x['tweet_text'], keep_words), axis=1)
    return df_copy, lower_matrix, upper_matrix

