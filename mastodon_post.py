from mastodon import Mastodon
from pytz import timezone
from os import path
import re
import datetime as dt
import markov_generator as mg

PATH = path.dirname(path.abspath(__file__))

if __name__ == "__main__":
    mastodon = Mastodon(
        client_id = PATH + "/token/clientcred.secret",
        access_token = PATH + "/token/usercred.secret",
        api_base_url = "https://gensokyo.town")

def pre_processing(sentence):
    """
    余分なものを取り除いたりマルコフ連鎖取り扱うための準備。
    """
    sentence = re.sub(r"\[EoS\]", "", sentence)#文末を表すのに使うので消す
    sentence = re.sub(r"<[^>]*?>", "", sentence)#HTMLタグ
    sentence = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)", "", sentence)#URL
    sentence = re.sub(r"[  \n\#]", "", sentence)#色々邪魔だったりする文字
    sentence = re.sub(r"&[a-zA-Z0-9]+;", "", sentence)#HTML特殊文字
    sentence = re.sub('([あ-んア-ン一-龥ー])\s+((?=[あ-んア-ン一-龥ー]))',r'\1\2', sentence)#日本語文字間の空白除去
    sentence = re.sub(r":[a-zA-Z0-9_-]+:", "", sentence)#絵文字
    sentence = re.sub(r"@[_a-zA-Z0-9]+", "", sentence)#リプライ
    return(sentence)

def get_toots():
    """
    Mastodonからtootを取得し、呟き内容を保存する。
    """
    #1日の始まりの時刻(JST)
    now = dt.datetime.now()
    end = timezone("Asia/Tokyo").localize(dt.datetime(now.year, now.month, now.day, now.hour, 15, 0, 0))
    start = end - dt.timedelta(hours=1)
    #tootの取得
    toots = mastodon.timeline(timeline="local", limit=40)
    while True:
        time = toots[-1]["created_at"].astimezone(timezone("Asia/Tokyo"))
        #取得したget_toots全てのtootが0:00より前の場合終了
        if time < start:
            break
        #追加でtootの取得
        toots = toots + mastodon.timeline(timeline="local", max_id=toots[-1]["id"]-1, limit=40)

    text = ""
    for toot in toots:
        #時間内のtootのみcontentを追加する
        time = toot["created_at"].astimezone(timezone("Asia/Tokyo"))
        if start <= time and time < end:
            #CWの呟きの場合隠されている方を追加せず表示されている方を追加する
            if toot["sensitive"] == True:
                sentence = pre_processing(toot["spoiler_text"])
                if sentence != "":
                    text += sentence + "\n"
            else:
                sentence = pre_processing(toot["content"])
                if sentence != "":
                    text += sentence + "\n"

    with open(PATH + "/text_file/toots.txt", 'a') as f:
        f.write(text)


if __name__ == "__main__":
    get_toots()
    with open(PATH + "/text_file/toots.txt", 'r') as f:
        text = f.read()
    with open(PATH + "/text_file/Akyu_words.txt", "r") as f:
        text += f.read()
    sentence = mg.sentence_generation(text)
    mastodon.status_post(status = sentence, visibility = "unlisted")
