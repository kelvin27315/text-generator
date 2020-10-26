import multiprocessing as mp
import MeCab


class TextGenerator:
    def __init__(self, text: str, n: int, mpara="", cpu_count=mp.cpu_count()-1):
        self.cpu_count = cpu_count
        self.n = n
        self.tagger = MeCab.Tagger(mpara)
        self.get_words_list(text)

    def word_split(self, sentence):
        """
        分かち書き
        """
        words = [word.split("\t")[0] for word in self.tagger.parse(sentence).splitlines()[:-1]]
        return(words.append("[EoS]"))

    def get_words_list(self, text):
        sentence_head = []
        words = []
        sentence_head_app = sentence_head.append
        words_ext = words.extend
        #1行(1文)ごとに分かち書きを行い、その末尾に[EoS]をつけて次のを繋げていく
        with mp.Pool(self.cpu_count()) as p:
            for wakachi in p.imap_unordered(word_split, text.splitlines()):
                if len(wakachi) >= self.n:
                    words_ext(wakachi)
                    sentence_head_app(wakachi[:self.n])
        self.words = words
        self.sentence_head = sentence_head