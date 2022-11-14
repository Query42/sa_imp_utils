from dispatcher import Dispatcher
from thread_reader import Thread

dispatcher = Dispatcher()
dispatcher.login(required=False)

club_thread = Thread(dispatcher, dispatcher.izgc_thread_id())
club_thread.report_new_trophies()
