from textgenerator.markov import MarkovChainForTextGen
from mstdn import Ponytail_Counter

def main():
    kasaki = Ponytail_Counter(id=22674, deltaday=1, url="https://example.com")
    with open("text.txt", "r") as f:
        text = f.read()
    markov = MarkovChainForTextGen(text, 3)
    post = markov.markov_chain()
    post += " #bot"
    kasaki.status_post(status=post, visibility="unlisted")

if __name__ == "__main__":
    main()