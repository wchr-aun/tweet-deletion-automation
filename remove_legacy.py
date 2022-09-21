from datetime import datetime, timedelta, timezone
import pandas as pd
from twitter_api import TwitterAPI
from tqdm import tqdm

twit = TwitterAPI()
tweets = pd.read_json('./data/tweet.json')
count = 0
DAYS_TO_KEEP = 30
cutoff_date = datetime.now(timezone.utc) - timedelta(days=DAYS_TO_KEEP)

for tweet in tqdm(tweets.tweet):
    if datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y') > cutoff_date:
        continue
    twit.del_tweet(tweet['id'])
    count += 1


print(f'{count} tweets deleted')
