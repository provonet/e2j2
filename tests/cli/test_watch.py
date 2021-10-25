from mock import patch
from e2j2 import cli
import pytest


@pytest.fixture(autouse=True)
def display_mocker():
    with patch("e2j2.cli.write"):
        yield


@pytest.fixture(autouse=True)
def repeat_once():
    with patch("e2j2.cli.repeat") as repeat_mocker:
        repeat_mocker.side_effect = [True, False]
        yield


@pytest.fixture()
def thread_mocker():
    with patch("e2j2.cli.Thread") as thread_mocker:
        yield thread_mocker


@patch("e2j2.cli.get_vars")
def test_watch_initial_run_not_set(get_vars_mocker, thread_mocker, argument_parser):
    args = argument_parser
    args.initial_run = False
    args.watchlist = "FOOBAR"
    args.run = ["foobar.sh"]
    config = cli.configure(args)

    get_vars_mocker.return_value = {"FOOBAR": "foobar"}

    cli.watch(config)
    args = thread_mocker.call_args[1]
    assert args['args'][0]['run'] == []


@patch("e2j2.cli.get_vars")
def test_watch_initial_run_set(get_vars_mocker, thread_mocker, argument_parser):
    args = argument_parser
    args.initial_run = True
    args.watchlist = "FOOBAR"
    args.run = ["foobar.sh"]
    config = cli.configure(args)

    get_vars_mocker.return_value = {"FOOBAR": "foobar"}

    cli.watch(config)
    args = thread_mocker.call_args[1]
    assert args['args'][0]['run'] == ['foobar.sh']


@patch("e2j2.cli.get_vars")
@patch("e2j2.cli.repeat")
def test_unchanged(repeat_mocker, get_vars_mocker, argument_parser):
    args = argument_parser
    args.initial_run = False
    args.splay = 0
    args.watchlist = "FOOBAR"
    args.run = ["foobar.sh"]
    config = cli.configure(args)

    repeat_mocker.side_effect = [True, True, False]
    get_vars_mocker.side_effect = [{"FOOBAR": "foobar"}, {"FOOBAR": "foobar"}]

    # sleep should be called if there are no changes
    with patch('e2j2.cli.sleep') as sleep_mocker:
        cli.watch(config)
        sleep_mocker.assert_called_with(1)


@patch("e2j2.cli.write")
@patch("e2j2.cli.get_vars")
def test_fail_keyerror(get_vars_mocker, display_mocker, argument_parser):
    args = argument_parser
    args.initial_run = True
    args.watchlist = "FOOBAR"
    args.run = ["foobar.sh"]
    get_vars_mocker.side_effect = KeyError('FOOBAR')
    config = cli.configure(args)
    cli.watch(config)
    assert "ERROR unknown key 'FOOBAR' in watchlist" in display_mocker.call_args[0][0]
