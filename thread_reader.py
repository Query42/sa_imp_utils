"""Functionality for reading a thread and parsing out new posts for use"""

import re
import time
from dataclasses import dataclass

from bs4 import BeautifulSoup

class ThreadNotFoundError(Exception):
    pass

class Thread:
    def __init__(self, dispatcher, thread_id):
        self.session = dispatcher.session
        self.dispatcher = dispatcher
        self.thread = thread_id
        try:
            thread_attrs = dispatcher.config[self.thread]
            self.page_number = int(thread_attrs["page"])
            self.last_post = int(thread_attrs["last_post"])
        except KeyError:
            print("No previous endpoint of thread in config. Saving new end.")
            self.page_number = self.get_last_page_number()
            self.last_post = len(self.get_page().posts)
            self.update_config_values()

    def get_page(self):
        # print(f"Fetching page {self.page_number} in thread {self.thread}.")
        payload = {"threadid": self.thread, "pagenumber": str(self.page_number)}
        response = self.session.get(
            "https://forums.somethingawful.com/showthread.php", params=payload)
        raw_page = response.text
        if "Specified thread was not found in the live forums." in raw_page:
            raise ThreadNotFoundError(f"Thread {self.thread} not accessible.")
        elif "The page number you requested" in raw_page:
            print("Last page of thread reached.")
            self.page_number -= 1
            return
        else:
            print(f"Parsing posts from thread {self.thread}, "
            + f"page {self.page_number}")
            page = Page(raw_page)
            return page

    def get_last_page_number(self):
        # TODO: fix this so it uses proper url parameterization
        response = self.session.get(
            "https://forums.somethingawful.com/showthread.php?threadid=" +
            f"{self.thread}&goto=lastpost",
            allow_redirects = False
        )
        url = response.headers["Location"]
        page_number = int(re.findall(r"pagenumber=(\d+)", url)[0])

        return page_number

    def new_posts(self):
        # print(f"Fetching new posts from threadid {self.thread}.")

        new_posts = []
        # TODO: refactor this to call self instead of while loop
        while True:
            page = self.get_page()
            if not page:
                # Last page of thread reached, has 40 posts
                break

            new_last_post = len(page.posts)
            new_posts += page.posts[self.last_post:new_last_post]
            if new_last_post >= 40:
                # print(f"40 posts on page {self.page_number}.")
                # print("Incrementing page number and resetting postcount.")
                self.page_number += 1
                self.last_post = 0
                time.sleep(2)
            else:
                # Last page of thread reached
                self.last_post = new_last_post
                break

        if new_posts:
            self.update_config_values()
        else:
            print(f"No new posts in thread {self.thread}.")

        return new_posts

    def report_new_trophies(self, eligible_trophies):
        imp_trophies = {}
        post_list = self.new_posts()

        for post in post_list:
            post.remove_quotes()
            trophies = post.trophies(eligible_trophies)
            if trophies:
                if post.username not in imp_trophies:
                    imp_trophies[post.username] = []

                imp_trophies[post.username] += trophies

        if imp_trophies:
            print("******** NEW TROPHIES ********")
            for imp, trophies in imp_trophies.items():
                print(f"{imp}: {'; '.join(trophies)}")
        else:
            print("No new trophies found.")

    def update_config_values(self):
        self.dispatcher.config[self.thread] = {
            "page": self.page_number,
            "last_post": self.last_post
        }
        self.dispatcher.save_config()


@dataclass
class Page:
    def __init__(self, raw_page):
        soup = BeautifulSoup(raw_page, "html.parser")
        self.posts = []
        self.unread_posts = []
        self.read_posts = []

        raw_posts = soup.find_all("table")
        for raw_post in raw_posts:
            post = Post(raw_post)
            if post.username == "Adbot":
                continue
            self.posts.append(post)
            if post.unread:
                self.unread_posts.append(post)
            else:
                self.read_posts.append(post)


class Post:
    def __init__(self, raw_post):
        self.raw_post = raw_post
        # Read posts have a first tr with class "seen1" or "seen2"
        # Unread posts have "altcolor1" or "altcolor2"
        # Use matching for unread so if this breaks all posts default to read
        # Might be a better way to do this by parsing redirect
        self.unread = "altcolor" in raw_post.tr["class"][0]

        self.cells = raw_post.find_all("td")
        user_info = self.cells[0]
        self.username = user_info.dt.get_text()
        # TODO: add handling for users with no avatar
        # TODO: check behavior here for users with gangtags, etc
        # Disabling for now as this may break for users with no avatar
        # self.avatar_url = user_info.img["src"]
        # TODO: fix this line
        # self.timestamp = cells.get_text()
        self.body = self.cells[1]

    def text(self):
        return self.body.get_text()

    def remove_quotes(self):
        quotes = self.body.find_all("div", "bbc-block")
        for quote in quotes:
            quote.decompose()

    def image_urls(self):
        images = self.body.find_all("img")
        return list(map(lambda img: img["src"], images))

    def trophies(self, eligible_trophies):
        earned_trophies = []
        images = self.image_urls()
        for trophy_id, trophy_text in eligible_trophies.items():
            for image in images:
                if re.search(f"i.imgur.com/{trophy_id}", image):
                    earned_trophies.append(trophy_text)

        return earned_trophies
