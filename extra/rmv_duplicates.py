##Removes duplicate tweets after pulling
import pandas as pd
import sys

file_name = sys.argv[1]
df = pd.read_csv(file_name)
df = df.drop_duplicates(subset='tweet_text', keep='first')
df.to_csv(file_name, columns=[df.columns[1],df.columns[2],df.columns[3]])
