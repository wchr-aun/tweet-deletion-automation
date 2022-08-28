import tweepy
from decouple import config


class TwitterAPI:
    def __init__(self) -> None:
        API_KEY = config('API_KEY')
        API_SECRET_KEY = config('API_SECRET_KEY')
        ACCESS_TOKEN = config('ACCESS_TOKEN')
        ACCESS_SECRET_TOKEN = config('ACCESS_SECRET_TOKEN')
        SCREEN_NAME = config('SCREEN_NAME')

        auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET_TOKEN)

        self.api = tweepy.API(auth)
        self.myID = self.api.get_user(screen_name=SCREEN_NAME).id

    def get_tweet(self, id: str) -> str:
        try:
            return self.api.get_status(id).text
        except Exception as e:
            return str(e)

    def del_tweet(self, id: str) -> bool:
        try:
            self.api.destroy_status(id)
            return True
        except Exception as e:
            if 'No status found with that ID.' in str(e):
                return True
            else:
                return False

    def get_my_tweets(self):
        return tweepy.Cursor(self.api.user_timeline, tweet_mode="extended").items()
