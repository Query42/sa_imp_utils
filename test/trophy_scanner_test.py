import trophy_scanner


def test_report_no_trophies_prints(capsys):
    trophy_scanner.report_new_trophies(None)
    assert capsys.readouterr().out != ""
