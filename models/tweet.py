from datetime import datetime
from typing import Optional, Dict, List


class MentionedTweet(Dict):
    in_reply_to_status_id: str
    in_reply_to_screen_name: str
    in_reply_text: str


class Tweet(Dict):
    created_at: datetime
    text: str
    mentioned_tweet: Optional[MentionedTweet]
    img_path: Optional[List[str]]
    favorite_count: int
    retweet_count: int
    retweet_source: Optional[str]
