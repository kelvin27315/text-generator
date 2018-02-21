from requests_oauthlib import OAuth1Session
from os import path
import json
import re
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

def pre_processing(sentence):
    """
    余分なものを取り除いたり準備。
    """
    sentence = re.sub(r"\[EoS\]", "", sentence)#文末を表すのに使うので消す
    sentence = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)", "", sentence)#URL
    sentence = re.sub(r"[  \n\#]", "", sentence)#色々邪魔だったりする文字
    sentence = re.sub(r"RT @[_a-zA-Z0-9]+: ", "", sentence)#RTされたtweetを取得するとくっついてくる
    sentence = re.sub(r"@[_a-zA-Z0-9]+", "", sentence)#リプライ
    sentence = re.sub('([あ-んア-ン一-龥ー])\s+((?=[あ-んア-ン一-龥ー]))',r'\1\2', sentence)#日本語文字間の空白除去
    return(sentence)

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
    for i in range(2):
        req = twitter.get(
            url = "https://api.twitter.com/1.1/statuses/home_timeline.json",
            params = {"count": 200, "max_id": tweets[-1]["id"]}
        )
        tweets += json.loads(req.text)
    text = ""
    #getしたtweetをいい具合に処理してから保存
    for tweet in tweets:
        sentence = pre_processing(tweet["text"])
        if sentence != "":
            text += sentence + "\n"

    #getしたtweetの文章のみを保存
    with open(PATH + "/text_file/tweets.txt", "w") as f:
        f.write(text)
    return(text)


if __name__ == "__main__":
    text = get_tweets()
    with open(PATH + "/text_file/Akyu_words.txt", "r") as f:
        text += f.read()
    sentence = mg.sentence_generation(text)
    req = twitter.post(
        url = "https://api.twitter.com/1.1/statuses/update.json",
        params = {"status": sentence}
    )
