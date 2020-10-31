from textgenerator.normalize_neologd import pre_processing
from mastodon import Mastodon
from pytz import timezone
from pathlib import Path
import datetime as dt
from time import sleep


class Ponytail_Counter(Mastodon):
    def __init__(self, id, url, deltaday=1):
        self.path = Path(__file__).parent.resolve()
        self.id = id

        today = dt.date.today()
        yesterday = today - dt.timedelta(days=deltaday)
        self.day_start = timezone("Asia/Tokyo").localize(dt.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0))
        self.day_end = timezone("Asia/Tokyo").localize(dt.datetime(today.year, today.month, today.day, 0, 0, 0, 0))

        super(Ponytail_Counter, self).__init__(
            client_id = self.path/"token"/"clientcred.secret",
            access_token = self.path/"token"/"usercred.secret",
            api_base_url = url
        )

    def get_toots(self):
        #tootの取得
        toots = self.account_statuses(id=self.id, limit=40)
        while toots[-1]["created_at"].astimezone(timezone("Asia/Tokyo")) > self.day_start:
            sleep(1)
            toots += self.account_statuses(id=self.id, max_id=toots[-1]["id"]-1, limit=40)

        text = ""
        for toot in toots:
            time = toot["created_at"].astimezone(timezone("Asia/Tokyo"))
            if self.day_start <= time and time < self.day_end:
                for content in [toot["content"], toot["spoiler_text"]]:
                    temp = pre_processing(content)
                    if len(temp) != 0:
                        text += "\n{}".format(temp)

        with open(self.path/"text.txt", "a") as f:
            f.write(text[1:])