from .text_generator import TextGenerator
import multiprocessing as mp
import random
import re


class MarkovChainForTextGen(TextGenerator):
    def __init__(self, text, ngram, cpu_count=mp.cpu_count()-1):
        super().__init__(text, ngram, cpu_count)
        self.get_markov_table()

    def get_markov_table(self):
        markov = {}
        state = tuple([self.words[i] for i in range(self.n-1)])
        for word in self.words[self.n-1:]:
            if state not in markov:
                markov[state] = []
            markov[state].append(word)
            state = list(state[1:])
            state.append(word)
            state = tuple(state)
        self.markov = markov

    def markov_chain(self, max_num_of_char=140):
        """
        マルコフ連鎖を行い、文を作る。
        """
        while True:
            sentence = ""
            state = random.choice(self.sentence_heads)
            for node in state:
                sentence += node

            while len(sentence) < max_num_of_char:
                #新規単語取得
                word = random.choice(self.markov[state])
                sentence += word
                if word == "[EoS]":
                    break

                #状態の更新
                state = list(state[1:])
                state.append(word)
                state = tuple(state)

            if len(sentence) < max_num_of_char:
                return(re.sub(r"\[EoS\]", "", sentence))