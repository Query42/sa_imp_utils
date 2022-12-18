"""Functionality for reading a thread and parsing out new posts for use"""

import re
import time
from dataclasses import dataclass

from bs4 import BeautifulSoup


class ThreadNotFoundError(Exception):
    pass


def scrape_page_number(response):
    url = response.headers["Location"]
    return int(re.findall(r"pagenumber=(\d+)", url)[0])


class Thread:
    def __init__(self, *, dispatcher, thread_id):
        self.dispatcher = dispatcher
        self.thread = thread_id
        self.last_read_index = None
        try:
            thread_attrs = dispatcher.config[self.thread]
            self.page_number = int(thread_attrs["page"])
            self.last_post = int(thread_attrs["last_post"])
        except KeyError:
            print("No previous endpoint of thread in config. Saving new end.")
            self.get_last_read_index()
            self.page_number = self.get_last_page_number()
            self.last_post = self.get_last_post()
            self.set_last_read()
            self.update_config_values()

    def get_raw_page(self, page_number):
        payload = {
            "threadid": self.thread, "pagenumber": str(page_number)}
        return self.dispatcher.get_thread(params=payload)

    def get_page(self):
        raw_page = self.get_raw_page(self.page_number).text
        if "Specified thread was not found in the live forums." in raw_page:
            raise ThreadNotFoundError(f"Thread {self.thread} not accessible.")

        if "The page number you requested" in raw_page:
            print("Last page of thread reached.")
            self.page_number -= 1
            return None

        print(f"Parsing posts from thread {self.thread}, "
              + f"page {self.page_number}")
        page = Page(raw_page, self.thread, self.page_number)
        return page

    def get_last_page_number(self):
        payload = {"threadid": self.thread, "goto": "lastpost"}
        response = self.dispatcher.get_thread(params=payload,
                                              allow_redirects=False)
        return scrape_page_number(response)

    def get_last_post(self):
        raw_page = self.get_raw_page(self.page_number).text
        page = Page(raw_page, self.thread, self.page_number)
        return len(page.posts)

    def new_posts(self):
        new_posts = []
        self.get_last_read_index()

        while True:
            page = self.get_page()
            if not page:
                # Last page of thread reached, has 40 posts
                break

            new_last_post = len(page.posts)
            new_posts += page.posts[self.last_post:new_last_post]
            if new_last_post < 40:
                # Last page of thread reached
                self.last_post = new_last_post
                break

            self.page_number += 1
            self.last_post = 0
            # Wait so as not to flood server with requests
            time.sleep(1)

        if new_posts:
            self.update_config_values()
        else:
            print(f"No new posts in thread {self.thread}.")

        self.set_last_read()
        return new_posts

    def get_last_read_index(self):
        if not self.dispatcher.logged_in:
            return

        page_num_response = self.dispatcher.get_thread(
            params={"threadid": self.thread, "goto": "newpost"},
            allow_redirects=False)
        unread_page_number = scrape_page_number(page_num_response)

        page_response = self.get_raw_page(unread_page_number)
        page = Page(page_response.text, self.thread, unread_page_number)
        if page.read_posts:
            self.last_read_index = page.read_posts[-1].index
        else:
            # Last read post was last post of prev page, or thread is unread
            prev_page_number = unread_page_number - 1
            prev_page_response = self.get_raw_page(prev_page_number)
            prev_page = Page(
                prev_page_response.text, self.thread, prev_page_number)
            if prev_page.read_posts:
                self.last_read_index = prev_page.read_posts[-1].index
            else:
                # Thread is unread. Best we can do is set it to one read post
                self.last_read_index = 1

    def set_last_read(self):
        if self.dispatcher.logged_in:
            self.dispatcher.get_thread(params={
                "action": "setseen",
                "threadid": self.thread,
                "index": self.last_read_index
            })

    def update_config_values(self):
        self.dispatcher.config[self.thread] = {
            "page": self.page_number,
            "last_post": self.last_post
        }
        self.dispatcher.save_config()


@dataclass
class Page:
    def __init__(self, raw_page, thread, number):
        self.thread = thread
        self.number = number
        self.soup = BeautifulSoup(raw_page, "html.parser")
        self.posts = []
        self.unread_posts = []
        self.read_posts = []

        raw_posts = self.soup.find_all("table")
        for raw_post in raw_posts:
            post = Post(raw_post, self.thread, self.number)
            if post.username == "Adbot":
                continue
            self.posts.append(post)
            if post.unread():
                self.unread_posts.append(post)
            else:
                self.read_posts.append(post)


# pylint: disable=too-many-instance-attributes
class Post:
    CELL_TAG = "td"

    def __init__(self, raw_post, thread, page_number):
        self.raw_post = raw_post
        self.thread = thread
        self.page_number = page_number

        self.cells = self.raw_post.find_all(self.CELL_TAG)
        self.username = self.raw_post.find(self.CELL_TAG, "userinfo").dt.text
        self.post_id = self.raw_post["id"]
        self.index = self.raw_post["data-idx"]
        self.timestamp = self.get_timestamp()
        self.body = self.raw_post.find(self.CELL_TAG, "postbody")

    def text(self):
        return self.body.get_text()

    def unread(self):
        # Read posts have a first "tr" with class "seen1" or "seen2"
        # Unread posts have "altcolor1" or "altcolor2"
        # Use matching for unread so if this breaks all posts default to read
        return "altcolor" in self.raw_post.tr["class"][0]

    def get_timestamp(self):
        try:
            raw = self.raw_post.find(self.CELL_TAG, "postdate").text
            # Remove the # and ? signs and extra whitespace
            return raw.translate({35: None, 63: None}).strip()
        except AttributeError:
            return "Parsing error. Could not parse timestamp."

    def get_avatar_url(self):
        # Always grabs actual avatar image. May need special case for Fungah!
        try:
            return self.raw_post.find(self.CELL_TAG, "userinfo").img["src"]
        # User has no avatar
        except TypeError:
            return ""

    def remove_quotes(self):
        quotes = self.body.find_all("div", "bbc-block")
        for quote in quotes:
            quote.decompose()

    def image_urls(self):
        images = self.body.find_all("img")
        return list(map(lambda img: img["src"], images))

    def link(self):
        return f"https://forums.somethingawful.com/showthread.php?threadid=" \
               f"{self.thread}&userid=0&perpage=40&pagenumber=" \
               f"{self.page_number}#{self.post_id}"
