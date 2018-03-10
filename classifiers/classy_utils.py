import gensim
from gensim import corpora, models, similarities
import pandas as pd

def build_freq_matrix(data_frame):
    ##Takes in the data from of dates, location, tweet text
    ##and returns a dataframe of words as columns, indexed by tweet text
    ##as rows. Each entry is the frequency of the word in that tweet.
    columns = data_frame.columns.values.tolist()
    tweets = data_frame.iloc[:, columns.index('tweet_text')].tolist()
    tweet_texts = tweets
    tweets = [str(tweet).strip().split(" ") for tweet in tweets]
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

def remove_words(dataframe, remove_words):
    df_copy = dataframe.copy()
    df_copy['tweet_text'] = dataframe.apply(lambda x: remove_from_tweet(x['tweet_text'], remove_words), axis=1)
    return df_copy

def remove_from_tweet(tweet, words):
    ##Remove words from the tweet texts if they're in list of words to remove
    tweet = str(tweet).split(" ")
    for word in tweet:
        if word in words:
            while word in tweet:
                tweet.remove(word)
    return " ".join(tweet)
    
def get_lower_upper(freq_matrix, lower_thresh, upper_thresh):
    ## Takes in the dataframe with date, location, and tweet text columns, a lower thresh decimal, a upper thresh decimal
    ## Then returns a new dataframe with the words that occur outside threshold * total tweets of upper and lower removed
    ## as well as the words below the lower threshold and above the upper threshold
    
    binary_matrix = freq_matrix.applymap(make_binary)
    sum_matrix = binary_matrix.apply(sum).to_frame()
    lower_cutoff = round(lower_thresh * len(freq_matrix))
    upper_cutoff = round(upper_thresh * len(freq_matrix))
    lower_matrix = sum_matrix.loc[sum_matrix[0] < lower_cutoff]
    upper_matrix = sum_matrix.loc[sum_matrix[0] > upper_cutoff]
    return lower_matrix, upper_matrix



