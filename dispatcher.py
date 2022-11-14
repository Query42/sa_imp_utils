"""Utilities for managing configuration and logging in to forums"""

import configparser
import json
import os

import requests
from bs4 import BeautifulSoup


class InvalidConfigError(Exception):
    pass


class Dispatcher:
    # May need to eventually refactor this into separate request handler and
    # config handler classes.
    SA_URL = "https://forums.somethingawful.com/"
    CONFIG_FILE = "config.ini"

    def __init__(self):
        self.session = requests.Session()
        self.config = configparser.ConfigParser(interpolation=None)
        if not os.path.isfile(self.CONFIG_FILE):
            raise InvalidConfigError(f"{self.CONFIG_FILE} is missing!")
        self.config.read(self.CONFIG_FILE)

    def check_sa_creds(self):
        if "username" not in self.config["DEFAULT"] \
                or "password" not in self.config["DEFAULT"] \
                or self.config["DEFAULT"]["username"] == "" \
                or self.config["DEFAULT"]["password"] == "":
            raise InvalidConfigError(
                f"username and password not present in {self.CONFIG_FILE}.")

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
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as file:
            self.config.write(file)

    # IZGC Thread parsing-related methods
    def izgc_thread_id(self):
        return self.config["DEFAULT"]["izgc_thread_id"]

    def get_izgc_trophies(self):
        # This should probably be in a config file, but I'm not putting it
        # there just so it's a little less visible to casual perusal.
        izgc_trophy_list_url = "https://impzone.club/alltrophies.html"
        trophy_dict = {}

        # Could modularize this, but it's YAGNI for now
        response = self.session.get(izgc_trophy_list_url)
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

    @staticmethod
    def report_new_trophies(imp_trophies):
        if not imp_trophies:
            return print("No new trophies found.")

        timestamp_file = "trophy_timestamps.json"
        try:
            with open(timestamp_file, "r") as file:
                trophy_log = json.load(file)
        except FileNotFoundError:
            trophy_log = {}

        print("\n******** NEW TROPHIES ********")
        for imp, trophies in imp_trophies.items():
            if imp not in trophy_log:
                new_member_string = " (New Club member!)"
                trophy_log[imp] = trophies
            else:
                new_member_string = ""
                for game, game_trophies in trophies.items():
                    if game not in trophy_log[imp]:
                        trophy_log[imp][game] = game_trophies
                    else:
                        trophy_log[imp][game].update(game_trophies)

            print(f"{imp}{new_member_string}:")
            for game, trophy in trophies.items():
                for name, timestamp in trophy.items():
                    print(f"[{game}] {name} -- posted {timestamp}")

        with open(timestamp_file, "w", encoding="utf-8") as file:
            json.dump(trophy_log, file, indent=2)
