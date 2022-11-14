import sys

from dispatcher import Dispatcher
from thread_reader import Thread

dispatcher = Dispatcher()
dispatcher.login(required=False)

club_thread = Thread(dispatcher, dispatcher.izgc_thread_id())

# Accept command line argument to read all pages
if "--all-pages" in sys.argv:
    club_thread.page_number = 1
    club_thread.last_post = 0

club_thread.trophy_scan()
