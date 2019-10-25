from __future__ import unicode_literals
from requests_oauthlib import OAuth1Session
from os import path
import unicodedata
import MeCab
import json
import re
import Normalize_neologd as nn
import markov_generator as mg

PATH = path.dirname(path.abspath(__file__))

if __name__ == "__main__":
    with open(PATH + "/token/twitter_token.secret", "r") as f:
        date = f.read()
    token = date.split("\n")
    twitter = OAuth1Session(
        client_key=token[0],
        client_secret=token[1],
        resource_owner_key=token[2],
        resource_owner_secret=token[3]
    )


def get_tweets():
    """
    tweetの取得から保存まで。
    """
    #user_timelineからtweetを取得
    req = twitter.get(
        url = "https://api.twitter.com/1.1/statuses/home_timeline.json",
        params = {"count": 200}
    )
    tweets = json.loads(req.text)
    for i in range(10):
        req = twitter.get(
            url = "https://api.twitter.com/1.1/statuses/home_timeline.json",
            params = {"count": 200, "max_id": tweets[-1]["id"]-1}
        )
        tweets += json.loads(req.text)

    text = ""
    #getしたtweetをいい具合に処理してから保存
    for tweet in tweets:
        if "今日のツイライフ" not in tweet["source"]:#いらないよね
            sentence = nn.pre_processing(tweet["text"])
            sentence = re.sub('RT:', '', sentence)
            if sentence != "":
                text += sentence + "\n"

    #getしたtweetの文章のみを保存
    with open(PATH + "/text_file/tweets.txt", "w") as f:
        f.write(text)
    return(text)


if __name__ == "__main__":
    text = get_tweets()
    #twitterで取得したものに、阿求の台詞足すよ
    with open(PATH + "/text_file/Akyu_words.txt", "r") as f:
        text += f.read()
    #文作るよ
    sentence = mg.sentence_generation(text)
    #投稿
    req = twitter.post(
        url = "https://api.twitter.com/1.1/statuses/update.json",
        params = {"status": sentence}
    )
