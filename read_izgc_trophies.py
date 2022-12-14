import sys

from dispatcher import Dispatcher
from trophy_scanner import TrophyReporter, IZGCThread

dispatcher = Dispatcher()
dispatcher.login(required=False)
club_thread = IZGCThread(dispatcher=dispatcher)

# Accept command line argument to read all pages
if "--all-pages" in sys.argv:
    club_thread.page_number = 1
    club_thread.last_post = 0

imp_trophies = club_thread.trophy_scan()
reporter = TrophyReporter(imp_trophies)
reporter.report_new_trophies()
