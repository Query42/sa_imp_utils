from dispatcher import Dispatcher
from thread_reader import Thread

dispatcher = Dispatcher()
dispatcher.login(required = False)

club_thread = Thread(dispatcher, dispatcher.izgc_thread_id())
club_thread.page_number = 239

# TODO: parse current trophies from club site and/or config
tracked_trophies = {
    "yK5gFgO": "Beat the game",
    "PaduUha": "Finish every level, including secrets (31 on the save screen)"
    }

club_thread.report_new_trophies(tracked_trophies)
