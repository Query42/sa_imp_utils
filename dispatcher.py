"""Utilities for managing configuration and logging in to forums"""

import configparser
import os

import requests


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

    def izgc_thread_id(self):
        return self.config["DEFAULT"]["izgc_thread_id"]

    def save_config(self):
        with open("config.ini", "w", encoding="utf-8") as file:
            self.config.write(file)
