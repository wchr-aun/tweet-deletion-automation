from models.tweet import Tweet, MentionedTweet
from twitter_api import TwitterAPI
from firebase import Firebase

from datetime import datetime, timedelta, timezone
from typing import List
from tqdm import tqdm
from requests import get
from os import remove

DAYS_TO_KEEP = 30
IMPORTANT_FLAG = '!important'

twit = TwitterAPI()
client = Firebase()


def get_img_path(tweet) -> List[str]:
    if 'media' not in tweet._json['entities']:
        return None
    media_url = [media['media_url_https'] for media in tweet.entities['media']]
    img_paths = []
    for url in media_url:
        img_data = get(url).content
        filename = url.split('/')[-1]
        img_path = f"media/{tweet.id}-{filename}"
        with open(f'./{img_path}', 'wb') as handler:
            handler.write(img_data)  # download image to disk
        uploaded = client.upload_media(
            f'./{img_path}', f"{tweet.id}-{filename}")
        if uploaded:
            img_paths.append(img_path)
            remove(f'./{img_path}')  # remove the image from local storage
        else:
            raise Exception(f"Failed to upload media: {url}")
    return img_paths


def get_mentioned_tweet(tweet) -> MentionedTweet:
    if tweet.in_reply_to_status_id == None:
        return None
    return MentionedTweet(
        in_reply_to_status_id=tweet.in_reply_to_status_id,
        in_reply_to_screen_name=tweet.in_reply_to_screen_name,
        in_reply_text=twit.get_tweet(tweet.in_reply_to_status_id)
    )


def main():
    tweets = twit.get_my_tweets()
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=DAYS_TO_KEEP)
    count = 0
    for tweet in tqdm(tweets):
        if tweet.created_at.replace(tzinfo=timezone.utc) > cutoff_date:
            continue
        if tweet.full_text.startswith(IMPORTANT_FLAG):
            continue
        try:
            client.add_tweet(str(tweet.id), Tweet(
                created_at=tweet.created_at,
                text=tweet.full_text,
                mentioned_tweet=get_mentioned_tweet(tweet),
                img_path=get_img_path(tweet),
                favorite_count=tweet.favorite_count,
                retweet_count=tweet.retweet_count,
                retweet_source=tweet.retweeted_status.id if tweet.retweeted else None
            ))
            deleted = twit.del_tweet(tweet.id)
            if not deleted:
                raise Exception(f"Failed to delete tweet: {tweet.id}")
        except Exception as e:
            print(f'Failed to add tweet {tweet.id}')
            print(e)
            continue

        count += 1

    print(f'{count} tweets deleted')


if __name__ == '__main__':
    main()
