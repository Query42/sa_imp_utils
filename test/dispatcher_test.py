import dispatcher

import io
import sys


def test_report_no_trophies_prints():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    dis = dispatcher.Dispatcher()
    dis.report_new_trophies(None)

    sys.stdout = sys.__stdout__
    assert captured_output.getvalue() != ""

