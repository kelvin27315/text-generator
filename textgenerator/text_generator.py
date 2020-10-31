import multiprocessing as mp
import MeCab


class TextGenerator:
    def __init__(self, text, ngram, cpu_count):
        self.cpu_count = cpu_count
        self.ngram = ngram
        self.get_words_list(text)

    def word_split(self, sentence):
        """
        分かち書き
        """
        tagger = MeCab.Tagger()
        words = [word.split("\t")[0] for word in tagger.parse(sentence).splitlines()[:-1]]
        words.append("[EoS]")
        return(tuple(words))

    def get_words_list(self, text):
        sentence_heads = []
        words = []
        sentence_head_app = sentence_heads.append
        words_ext = words.extend
        #1行(1文)ごとに分かち書きを行い、その末尾に[EoS]をつけて次のを繋げていく
        with mp.Pool(self.cpu_count) as p:
            for wakachi in p.imap_unordered(self.word_split, text.splitlines()):
                if len(wakachi) >= self.ngram-1:
                    words_ext(wakachi)
                    sentence_head_app(wakachi[:self.ngram-1])
        self.words = words
        self.sentence_heads = sentence_heads