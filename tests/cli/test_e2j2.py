import pytest
from  mock import patch
from e2j2 import cli
from e2j2.exceptions import E2j2Exception


@pytest.fixture(autouse=True)
def display_mocker():
    with patch("e2j2.cli.write"):
        yield


@patch('e2j2.cli.arg_parse')
@patch('e2j2.cli.run')
def test_e2j2(run_mocker, arg_mocker, argument_parser):
    arg_mocker.return_value = argument_parser
    config = cli.configure(argument_parser)
    run_mocker.return_value = 0
    error_code = cli.e2j2()
    run_mocker.assert_called_with(config)
    assert error_code == 0


@patch('e2j2.cli.arg_parse')
@patch('e2j2.cli.watch')
def test_e2j2_watch_option_set(watch_mocker, arg_mocker, argument_parser):
    args = argument_parser
    args.watchlist = "FOOBAR"
    arg_mocker.return_value = args
    config = cli.configure(argument_parser)

    cli.e2j2()
    watch_mocker.assert_called_with(config)


@patch('e2j2.cli.arg_parse')
@patch('e2j2.cli.configure')
@patch("e2j2.cli.write")
def test_e2j2_config_error(display_mocker, configure_mocker, arg_mocker, argument_parser):
    args = argument_parser
    args.stacktrace = True
    arg_mocker.return_value = args
    arg_mocker.return_value = argument_parser
    configure_mocker.side_effect = E2j2Exception('some error')
    error_code = cli.e2j2()
    assert error_code == 1
