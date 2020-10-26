from mastodon import Mastodon
from pytz import timezone
from pathlib import Path
import datetime as dt
import pandas as pd


class Ponytail_Counter(Mastodon):
    def __init__(self, dd=1, id=22674):
        self.path = Path(__file__).parent.resolve()
        self.id = id
        self.ponytail = 0
        self.kedama = 0

        today = dt.date.today()
        self.yesterday = today - dt.timedelta(days=1)
        #1日の始まりの時刻(JST)
        self.day_start = timezone("Asia/Tokyo").localize(dt.datetime(self.yesterday.year, self.yesterday.month, self.yesterday.day, 0, 0, 0, 0))
        #1日の終わりの時刻(JST)
        self.day_end = timezone("Asia/Tokyo").localize(dt.datetime(today.year, today.month, today.day, 0, 0, 0, 0))

        super(Ponytail_Counter, self).__init__(
            client_id = self.path/"token"/"clientcred.secret",
            access_token = self.path/"token"/"usercred.secret",
            api_base_url = "https://mstdn.poyo.me"
        )

    def get_toots(self):
        #tootの取得
        toots = self.account_statuses(id=self.id, limit=40)
        while toots[-1]["created_at"].astimezone(timezone("Asia/Tokyo")) > self.day_start:
            toots += self.account_statuses(id=self.id, max_id=toots[-1]["id"]-1, limit=40)

        text = ""
        for toot in toots:
            time = toot["created_at"].astimezone(timezone("Asia/Tokyo"))
            if self.day_start <= time and time < self.day_end:
                text += "{} {}".format(toot["content"], toot["spoiler_text"])

        with open("text.txt") as f:
            f.write(text)

    def post(self):
        """
        投稿
        """
        user = self.account(self.id)
        self.status_post(status=post, visibility="unlisted")


def main():
    kasaki = Ponytail_Counter()
    kasaki.get_toots()
    kasaki.post()

if __name__ == "__main__":
    main()