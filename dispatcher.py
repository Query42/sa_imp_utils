"""Utilities for managing configuration and logging in to forums"""

import configparser
import os

import requests
from bs4 import BeautifulSoup


class InvalidConfigError(Exception):
    pass


class Dispatcher:
    # May need to eventually refactor this into separate request handler and
    # config handler classes.
    SA_URL = "https://forums.somethingawful.com/"

    def __init__(self):
        self.session = requests.Session()
        self.config = configparser.ConfigParser(interpolation=None)
        if not os.path.isfile("config.ini"):
            raise InvalidConfigError("config.ini is missing!")
        self.config.read("config.ini")

    def check_sa_creds(self):
        if "username" not in self.config["DEFAULT"] \
                or "password" not in self.config["DEFAULT"] \
                or self.config["DEFAULT"]["username"] == "" \
                or self.config["DEFAULT"]["password"] == "":
            raise InvalidConfigError(
                "username and password not present in config.ini.")

    def login(self, required=True):
        try:
            self.check_sa_creds()
        except InvalidConfigError:
            if required:
                raise
            else:
                return print(
                    "Warning! Cannot proceed with login, continuing as " +
                    "anonymous user."
                )

        info = {"username": self.config["DEFAULT"]["username"],
                "password": self.config["DEFAULT"]["password"],
                "action": "login"
                }
        self.session.post(
            f"{self.SA_URL}account.php", data=info)

    def get_thread(self, **kwargs):
        return self.session.get(f"{self.SA_URL}showthread.php", **kwargs)

    def save_config(self):
        with open("config.ini", "w", encoding="utf-8") as file:
            self.config.write(file)

    # IZGC Thread parsing-related methods
    def izgc_thread_id(self):
        return self.config["DEFAULT"]["izgc_thread_id"]

    def get_izgc_trophies(self):
        # This should probably be in a config file, but I'm not putting it
        # there just so it's a little less visible to casual perusal.
        IZGC_TROPHY_LIST_URL = "https://impzone.club/alltrophies.html"
        trophy_dict = {}

        # Could modularize this, but it's YAGNI for now
        response = self.session.get(IZGC_TROPHY_LIST_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        trophies = soup.find_all("div", "item-trophy tooltip")
        for trophy in trophies:
            try:
                trophy_info_strings = tuple(trophy.stripped_strings)
                game = trophy_info_strings[1]
                name = trophy_info_strings[0]
                trophy_data = {
                    "full_name": f"[{game}] {name}",
                    "game": game,
                    "name": name,
                    "system_year": trophy_info_strings[2]
                }
                trophy_dict[trophy["imgur_id"]] = trophy_data
            except KeyError:
                # No imgur id present, so we don't scan for it
                continue

        return trophy_dict
