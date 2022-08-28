import pandas as pd
from twitter_api import TwitterAPI
from tqdm import tqdm

twit = TwitterAPI()
tweets = pd.read_json('./data/tweet.json')
count = 0
f = open('./backup.txt', 'r')
deleted = f.read().split('\n')

for tweet in tqdm(tweets.tweet):
    if tweet['id'] in deleted:
        continue
    twit.del_tweet(tweet['id'])
    count += 1


print(f'{count} tweets deleted')
