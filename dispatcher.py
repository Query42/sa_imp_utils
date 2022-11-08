"""Utilities for managing configuration and logging in to forums"""

import configparser
import os

import requests

class InvalidConfigError(Exception):
    pass

class Dispatcher:
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

        info = { "username": self.config["DEFAULT"]["username"],
                "password": self.config["DEFAULT"]["password"],
                "action": "login"
                }
        self.session.post(
            "https://forums.somethingawful.com/account.php", data=info)

    def izgc_thread_id(self):
        return self.config["DEFAULT"]["izgc_thread_id"]

    def save_config(self):
        with open("config.ini", "w", encoding="utf-8") as file:
            self.config.write(file)
