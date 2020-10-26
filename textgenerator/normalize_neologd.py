from __future__ import unicode_literals
import unicodedata
import re

"""
このプログラムは形態素解析を行ったときにより正しく分割を行うために行う処理
"""

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

def pre_processing(text):
    """
    余分なものを取り除いたりマルコフ連鎖取り扱うための準備。
    """
    text = normalize_neologd(text)
    text = re.sub(r"\[EoS\]", "", text)#文末を表すのに使うので消す
    text = re.sub(r"<[^>]*?>", "", text)#HTMLタグ
    text = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)", "", text)#URL
    #LSEP RSEPとか文字の流れを反転するやつを消す
    text = re.sub(r"[\#  ‮]", "", text)
    text = re.sub(r"\n", "", text)#Quesdon経由だと改行が何故か残ってる
    text = re.sub(r"RT @[_a-zA-Z0-9]+: ", "", text)#RTされたtweetを取得するとくっついてくる
    text = re.sub(r"&[a-zA-Z0-9]+;", "", text)#HTML特殊文字
    text = re.sub(r":[a-zA-Z0-9_-]+:", "", text)#絵文字
    text = re.sub(r"@[_a-zA-Z0-9]+", "", text)#リプライ
    return(text)
