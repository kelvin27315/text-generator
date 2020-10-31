from mstdn import Ponytail_Counter

def main():
    kasaki = Ponytail_Counter(id=22674, url="https://example.com", deltaday=1)
    kasaki.get_toots()


if __name__ == "__main__":
    main()