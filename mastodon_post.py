from __future__ import unicode_literals
from mastodon import Mastodon
from pytz import timezone
from os import path
import re
import unicodedata
import datetime as dt
import markov_generator as mg

PATH = path.dirname(path.abspath(__file__))

if __name__ == "__main__":
    mastodon = Mastodon(
        client_id = PATH + "/token/clientcred.secret",
        access_token = PATH + "/token/usercred.secret",
        api_base_url = "https://gensokyo.town")

#下の関数3つ
#https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp.ja
def unicode_normalize(cls, s):
    pt = re.compile('([{}]+)'.format(cls))

    def norm(c):
        return unicodedata.normalize('NFKC', c) if pt.match(c) else c

    s = ''.join(norm(x) for x in re.split(pt, s))
    s = re.sub('－', '-', s)
    return s

def remove_extra_spaces(s):
    s = re.sub('[ 　]+', ' ', s)
    blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
                      '\u3040-\u309F',  # HIRAGANA
                      '\u30A0-\u30FF',  # KATAKANA
                      '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
                      '\uFF00-\uFFEF'   # HALFWIDTH AND FULLWIDTH FORMS
                      ))
    basic_latin = '\u0000-\u007F'

    def remove_space_between(cls1, cls2, s):
        p = re.compile('([{}]) ([{}])'.format(cls1, cls2))
        while p.search(s):
            s = p.sub(r'\1\2', s)
        return s

    s = remove_space_between(blocks, blocks, s)
    s = remove_space_between(blocks, basic_latin, s)
    s = remove_space_between(basic_latin, blocks, s)
    return s

def normalize_neologd(s):
    s = s.strip()
    s = unicode_normalize('０-９Ａ-Ｚａ-ｚ｡-ﾟ', s)

    def maketrans(f, t):
        return {ord(x): ord(y) for x, y in zip(f, t)}

    s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)  # normalize hyphens
    s = re.sub('[﹣－ｰ—―─━ー]+', 'ー', s)  # normalize choonpus
    s = re.sub('[~∼∾〜〰～]', '', s)  # remove tildes
    s = s.translate(
        maketrans('!"#$%&\'()*+,-./:;<=>?@[¥]^_`{|}~｡､･｢｣',
              '！”＃＄％＆’（）＊＋，－．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))

    s = remove_extra_spaces(s)
    s = unicode_normalize('！”＃＄％＆’（）＊＋，－．／：；＜＞？＠［￥］＾＿｀｛｜｝〜', s)  # keep ＝,・,「,」
    s = re.sub('[’]', '\'', s)
    s = re.sub('[”]', '"', s)
    return s

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
    sentence = normalize_neologd(sentence)
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
