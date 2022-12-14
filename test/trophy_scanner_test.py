import pytest

import trophy_scanner


@pytest.fixture(name="mock_trophy_log")
def fixture_mock_trophy_log():
    pass


class TestTrophyReporter:
    def test_no_trophies_prints(self, capsys):
        trophy_scanner.report_new_trophies(None)
        assert capsys.readouterr().out != ""

    def test_no_existing_log_saves_all(self, mocker):
        mock_open = mocker.patch(
            "builtins.open",
            mocker.mock_open(read_data=""),
            side_effect=FileNotFoundError()
        )



