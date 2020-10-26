from text_generator import TextGenerator
import random


class MarkovChainForTextGen(TextGenerator):
    def __init__(self, text: str, n: int, mpara="", cpu_count=mp.cpu_count()-1):
        super(TextGenerator, self).__init__(text, n, mpara=, cpu_count)
        self.markov = self.get_markov_table()

    def get_markov_table(self):
        markov = {}
        state = tuple([self.words[i] for i in range(self.n-1)])
        for word in self.words[self.n-1:]:
            if state not in markov:
                markov[state] = []
            markov[state].append(word)
            state = [node for node in state[1:]]
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
                if word == "[EoS]" and random.random() > 0.7:
                    break
                else:
                    state = random.choice(self.sentence_heads)
                    for node in state:
                        sentence += node

                #状態の更新
                state = [node for node in state[1:]]
                state.append(word)
                state = tuple(state)

            if len(sentence) < max_num_of_char:
                return(re.sub(r"\[EoS\]", "", sentence))