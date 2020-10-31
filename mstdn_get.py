from mstdn import Ponytail_Counter

def main():
    kasaki = Ponytail_Counter(id=22674, deltaday=1, url="https://example.com")
    kasaki.get_toots()


if __name__ == "__main__":
    main()