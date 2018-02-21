from requests_oauthlib import OAuth1Session
from os import path
import MeCab
import json
import re
import markov_generator


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


def pre_processing(sentence):
    """
    余分なものを取り除いたり準備。
    """
    #URI, LSEP, RSEP, 改行, ハッシュタグ, RT表記, replyの除去, 日本語文字間の空白の除去
    sentence = re.sub(r"\[EoS\]", "", sentence)
    sentence = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)", "", sentence)
    sentence = re.sub(r"[  \n\#]", "", sentence)
    sentence = re.sub(r"RT @[_a-zA-Z0-9]+: ", "", sentence)
    sentence = re.sub(r"@[_a-zA-Z0-9]+", "", sentence)
    sentence = re.sub('([あ-んア-ン一-龥ー])\s+((?=[あ-んア-ン一-龥ー]))',r'\1\2', sentence)
    return(sentence)

def get_tweets():
    """
    tweetの取得から保存まで。
    """
    #user_timelineからtweetを取得
    req = twitter.get(
        url = "https://api.twitter.com/1.1/statuses/home_timeline.json",
        params = {"count": 100}
    )

    #getしたtweetをいい具合に処理してから保存
    text = ""
    if req.status_code == 200:
        tweets = json.loads(req.text)
        for tweet in tweets:
            sentence = pre_processing(tweet["text"])
            if sentence != "":
                text += sentence + "\n"

    #getしたtweetの文章のみを保存
    with open(PATH + "/text_file/tweets.txt", "w") as f:
        f.write(text)


if __name__ == "__main__":
    get_tweets()
