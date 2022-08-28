from firebase import Firebase
from twitter_api import TwitterAPI
from models.tweet import Tweet, MentionedTweet

from os import listdir
from decouple import config
from datetime import datetime
from tqdm import tqdm
from typing import List
import pandas as pd

STORE_MEDIA = True
LIMIT = 20000
twit = TwitterAPI()
BASE_DATA_PATH = './data'


def search_img(tweet_id: str, mediaList: list) -> List[str]:
    UNRELATED_ID = -20
    img_paths = []
    for i, c in enumerate(mediaList):
        if c[:UNRELATED_ID] == tweet_id:
            img_paths.append(f'media/{c}')
    return img_paths


def get_mentioned_tweet(tweet) -> MentionedTweet:
    if 'in_reply_to_status_id' not in tweet:
        return None
    return MentionedTweet(
        in_reply_to_status_id=tweet['in_reply_to_status_id'],
        in_reply_to_screen_name=tweet['in_reply_to_screen_name'] if 'in_reply_to_screen_name' in tweet else None,
        in_reply_text=twit.get_tweet(tweet['in_reply_to_status_id'])
    )


def backup_legacy():
    client = Firebase()
    mediaList = listdir(f'{BASE_DATA_PATH}/tweet_media')
    tweets = pd.read_json(f'{BASE_DATA_PATH}/tweet.json')
    count = 0

    f = open('backup.txt', 'r')
    backed_ids = f.read().split('\n')

    for tweet in tqdm(tweets.tweet):
        if tweet['id'] in backed_ids:
            continue
        if count >= LIMIT:
            break
        formatted = Tweet(
            created_at=datetime.strptime(
                tweet['created_at'].split(' ', 1)[1],
                '%b %d %H:%M:%S +0000 %Y'),
            text=tweet['full_text'],
            mentioned_tweet=get_mentioned_tweet(tweet),
            img_path=search_img(tweet['id'], mediaList),
            favorite_count=int(tweet['favorite_count']),
            retweet_count=int(tweet['retweet_count']),
            retweet_source=tweet['entities']['media'][0]['source_status_id']
            if tweet['full_text'].startswith('RT @') and 'media' in tweet['entities'] else None,
        )
        added = client.add_tweet(tweet['id'], formatted)
        if added:
            if STORE_MEDIA and formatted['img_path'] is not []:
                for url in formatted['img_path']:
                    filename = url.replace('media/', '')
                    client.upload_media(
                        f'{BASE_DATA_PATH}/tweet_media/{filename}', filename)
            f = open('backup.txt', 'a', encoding='utf8')
            f.write(tweet['id'] + '\n')
        count += 1


if __name__ == '__main__':
    backup_legacy()
