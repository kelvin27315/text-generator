from textgenerator.markov import MarkovChainForTextGen
from mstdn import Ponytail_Counter
from pathlib import Path

def main():
    kasaki = Ponytail_Counter(id=22674, url="https://example.com", deltaday=1)
    with open(Path(__file__).absolute()/"text.txt", "r") as f:
        text = f.read()
    markov = MarkovChainForTextGen(text, 3)
    post = markov.markov_chain()
    post += " #bot #markov3gram"
    kasaki.status_post(status=post, visibility="unlisted")

if __name__ == "__main__":
    main()