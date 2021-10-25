from mock import patch
from e2j2 import cli
import pytest


@pytest.fixture(autouse=True)
def display_mocker():
    with patch("e2j2.cli.write"):
        yield


@patch("e2j2.cli.run")
def test_watch_run(run_mocker, argument_parser):
    run_mocker.return_value = 0
    args = argument_parser
    config = cli.configure(args)
    exit_code = cli.watch_run(config)
    assert exit_code == 0
    assert run_mocker.call_count == 2


@patch("e2j2.cli.run")
def test_watch_run_noop_set(run_mocker, argument_parser):
    run_mocker.return_value = 0
    args = argument_parser
    args.noop = True
    config = cli.configure(args)
    exit_code = cli.watch_run(config)
    assert exit_code == 0
    assert run_mocker.call_count == 1


@patch("e2j2.cli.run")
def test_fail_watch_run(run_mocker, argument_parser):
    run_mocker.return_value = 1
    args = argument_parser
    config = cli.configure(args)
    exit_code = cli.watch_run(config)
    assert exit_code == 1
    assert run_mocker.call_count == 1
