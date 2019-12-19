import random
import MeCab
import re

def word_split(sentence, words, sentence_head):
    """
    引数に分かち書きかけて返すだけ
    """
    #MeCab(NEologd辞書使用)による分かち書き
    m = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd")
    #分かち書き
    one_sentence_head = []
    count = 0
    for word in m.parse(sentence).splitlines():
        if word != "EOS":
            if word.split("\t")[1].split(",")[1] == "代名詞" and word.split("\t")[1].split(",")[2] == "一般":
                word = re.sub("(おれ|オレ|われ|ワレ|わい|ワイ|ぼく|ボク|おら|オラ|おいら|オイラ|あたい|アタイ|あたし|わし|ワシ|わたくし)","わたし",word)
                word = re.sub("(われら|我ら|われわれ|我々|ぼくら|僕ら|ぼくたち|僕達|僕たち)","私達",word)
                word = re.sub("(俺|我|僕|儂|己|余)","私",word)
                word = re.sub("(おまえ|オマエ|お前|てめえ|てめぇ)","あんた",word)
                word = re.sub("(きみ|キミ)","あなた",word)
                word = re.sub("君","貴方",word)
            words.append(word.split('\t')[0])
            if count < 2:
                one_sentence_head.append(word.split('\t')[0])
            count += 1
    if 1 < len(one_sentence_head):
        sentence_head.append(tuple(one_sentence_head))
    return(words, sentence_head)


def markov_chain(words, sentence_head):
    """
    バイグラムでマルコフ連鎖を行い、文を作る。
    """
    #下準備でテーブルを作る
    markov = {}
    w1 = ""
    w2 = ""
    for word in words:
        if w1 and w2:
            if (w1, w2) not in markov:
                markov[(w1, w2)] = []
            markov[(w1, w2)].append(word)
        w1, w2, = w2, word

    #単語を繋げるところ
    while True:
        sentence = ""
        #ここのランダムチョイスをどこかの文の先頭にする。
        w1, w2 = random.choice(sentence_head)
        sentence += w1
        sentence += w2
        #140字超えたらやり直し
        while len(sentence) < 140:
            #はじめn個の単語の次の単語を選ぶ。同じ条件のをランダムに選ぶ
            temp = random.choice(markov[(w1, w2)])
            sentence += temp
            w1, w2, = w2, temp
            #もとの文での文末を引き当てたら確率で次の文を繋げるか決める
            if temp == "[EoS]":
                if random.random() > 0.3:
                    break
        #条件にあってたら[EoS]を取り除いて終了
        if len(sentence) < 140 and temp == "[EoS]":
            sentence = re.sub(r"\[EoS\]", ".", sentence)
            if sentence != ".":
                break
    return(sentence)


def sentence_generation(text):
    """
    文を作るよ
    """
    sentence_head = []
    words = []
    #1行(1文)ごとに分かち書きを行い、その末尾に[EoS]をつけて次のを繋げていく
    for sentence in text.splitlines():
        if sentence != "":
            words, sentence_head = word_split(sentence,words,sentence_head)
            words.append("[EoS]")
    #実際に文を作るところ
    #print(sentence_head)
    sentence = markov_chain(words, sentence_head)
    return(sentence)
