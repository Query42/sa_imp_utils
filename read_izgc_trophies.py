import sys

from dispatcher import Dispatcher
from trophy_scanner import report_new_trophies, IZGCThread

dispatcher = Dispatcher()
dispatcher.login(required=False)
club_thread = IZGCThread(dispatcher=dispatcher)

# Accept command line argument to read all pages
if "--all-pages" in sys.argv:
    club_thread.page_number = 1
    club_thread.last_post = 0

imp_trophies = club_thread.trophy_scan()
report_new_trophies(imp_trophies)
