import random
import MeCab
import re

def word_split(sentence):
    """
    引数に分かち書きかけて返すだけ
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
    """
    バイグラムでマルコフ連鎖を行い、文を作る。
    """
    #下準備でテーブルを作る
    markov = {}
    w1 = ""
    w2 = ""
    for word in words.split():
        if w1 and w2:
            if (w1, w2) not in markov:
                markov[(w1, w2)] = []
            markov[(w1, w2)].append(word)
        w1, w2, = w2, word

    #単語を繋げるところ
    while True:
        sentence = ""
        w1, w2 = random.choice(list(markov.keys()))
        #140字超えたらやり直し
        while len(sentence) < 140:
            temp = random.choice(markov[(w1, w2)])
            sentence += temp
            w1, w2, = w2, temp
            #もとの文での文末を引き当てたら確率で次の文を繋げるか決める
            if temp == "[EoS]":
                if random.random() > 0.3:
                    break
        #条件にあってたら[EoS]を取り除いて終了
        if len(sentence) < 140 and temp == "[EoS]":
            sentence = re.sub(r"\[EoS\]", "", sentence)
            if sentence != "":
                break
    return(sentence)


def sentence_generation(text):
    """
    文を作るよ
    """
    words = ""
    #1行(1文)ごとに分かち書きを行い、その末尾に[EoS]をつけて次のを繋げていく
    for sentence in text.splitlines():
        if sentence != "":
            words += word_split(sentence) + "[EoS] "
    #実際に文を作るところ
    sentence = markov_chain(words)
    return(sentence)
