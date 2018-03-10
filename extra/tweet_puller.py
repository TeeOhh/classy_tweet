##Analyzing tweets to determine U.S. positions on popular social/ethical issues

import twitter_utils as utils
import sys

## ----- Pulling code -----
utils.get_issue_tweets(sys.argv[1])
