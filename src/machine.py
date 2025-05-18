from abc import ABC
import datetime
import pytz
import utils
import storage
from config import config

SGT_TIMEZONE = pytz.timezone("Asia/Singapore")


class Machine(ABC):
    curr_user = None

    def __init__(self, house_id: str, name: str):
        self.name = name
        self.house_id = house_id

    def get_name(self):
        return self.name

    def status(self, mention_user: bool = True):
        curr_user, end_time = storage.get_laundry_timer(self.house_id, self.name)
        if utils.is_available(end_time):
            reply = f"AVAILABLE \U00002705"
            if curr_user:
                reply += f', last used by @{'' if mention_user else ' '}{curr_user} ({end_time.astimezone(SGT_TIMEZONE).strftime("%m/%Y %I:%M%p")})'
            return reply
        else:
            time_delta = end_time - datetime.datetime.now()
            time_in_min = time_delta.seconds // 60
            time_in_sec = time_delta.seconds % 60
            return f"UNAVAILABLE \U0000274C for {time_in_min}m {time_in_sec}s until {end_time.astimezone(SGT_TIMEZONE).strftime('%I:%M%p')} by @{curr_user}"

    def get_curr_user(self):
        curr_user, end_time = storage.get_laundry_timer(self.house_id, self.name)
        return curr_user

    def start_machine(
        self,
        new_user: str,
        chat_id: int,
        thread_id: int | None,
        duration_in_seconds: int,
    ):
        _, end_time = storage.get_laundry_timer(self.house_id, self.name)
        if not utils.is_available(end_time):
            return False
        else:
            new_end_time = datetime.datetime.now() + datetime.timedelta(
                seconds=duration_in_seconds * 60
            )
            new_curr_user = new_user
            storage.set_laundry_timer(
                self.house_id,
                self.name,
                new_curr_user,
                new_end_time,
                chat_id,
                thread_id,
            )
            return True
