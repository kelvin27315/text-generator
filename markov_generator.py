import random
import MeCab
import re

def word_split(sentence):
    """
    取得したtootのcontent類に分かち書きを行う。
    """
    #MeCab(NEologd辞書使用)による分かち書き
    m = MeCab.Tagger("-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")
    words = ""
    #分かち書き
    for word in m.parse(sentence).splitlines():
        if word != "EOS":
            words += word.split('\t')[0] + " "
    return(words)


def markov_chain(words):
    markov = {}
    w1 = ""
    w2 = ""
    for word in words.split():
        if w1 and w2:
            if (w1, w2) not in markov:
                markov[(w1, w2)] = []
            markov[(w1, w2)].append(word)
        w1, w2, = w2,  word

    sentence = ""
    #140字未満かつ、もとの分での文末([EoS]の目印)が最後に来ている場合、マルコフ連鎖での繋ぎを終了する
    while True:
        w1, w2 = random.choice(list(markov.keys()))
        while len(sentence) < 140:
            temp = random.choice(markov[(w1, w2)])
            sentence += temp
            w1, w2, = w2, temp
            if sentence[-5:] == "[EoS]":
                if random.random() > 0.3:
                    break
        if len(sentence) < 140 and sentence[-5:] == "[EoS]":
            sentence = re.sub(r"\[EoS\]", "", sentence)
            #初手て[EoS]を引いてそのまま出てきてしまった場合はやり直し
            if sentence != "":
                break
        sentence = ""
    return(sentence)

def sentence_generation(text):
    words = ""
    for sentence in text.splitlines():
        if sentence != "":
            words += word_split(sentence) + "[EoS] "
    sentence = markov_chain(words)
    return(sentence)
