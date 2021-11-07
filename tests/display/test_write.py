import pytest
from e2j2 import cache
from mock import patch
from e2j2 import display


@pytest.fixture(autouse=True)
def stderr_mocker():
    with patch("sys.stderr.write") as stderr_mocker:
       yield


def test_with_colors():
    display.colorize()
    assert display._colors.green == display.GREEN


def test_no_colors():
    display.no_colors()
    assert display._colors.green == ''


def test_write_new_line():
    cache.log_repeat_log_msg_counter = 0
    display.write('line of text')
    assert cache.last_log_line == 'line of text'
    assert cache.log_repeat_log_msg_counter == 1


def test_write_repeated_line():
    cache.log_repeat_log_msg_counter = 0
    cache.print_at = 3
    for _ in range(4):
        display.write('line of text')

    assert cache.log_repeat_log_msg_counter == 1

