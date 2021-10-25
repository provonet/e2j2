import pytest
from mock import patch
from e2j2 import cli

PROG_AND_VERSION = ('e2j2', '', 'x.x.x')


@pytest.fixture
def args(argument_parser):
    with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
        return cli.arg_parse(*PROG_AND_VERSION)


def test_arg_parse_searchlist(args):
    assert args.searchlist is None


def test_arg_parse_recursive(args):
    assert args.recursive is False


@patch('sys.stderr')
def test_arg_parse_conflict_searchlist_and_recurse(argument_parser_class):
    argument_parser = argument_parser_class()
    argument_parser.searchlist = []
    argument_parser.recursive = True
    with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
        with pytest.raises(SystemExit) as err:
            cli.arg_parse(*PROG_AND_VERSION)

        assert err.value.code == 2


@patch('sys.stderr')
def test_arg_parse_conflict_splay_and_empty_watchlist(argument_parser_class):
    argument_parser = argument_parser_class()
    argument_parser.splay = True
    argument_parser.watchlist = []
    with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
        with pytest.raises(SystemExit) as err:
            cli.arg_parse(*PROG_AND_VERSION)

        assert err.value.code == 2


@patch('sys.stderr')
def test_arg_parse_conflict_initial_run_and_empty_watchlist(argument_parser_class):
    argument_parser = argument_parser_class()
    argument_parser.initial_run = True
    argument_parser.watchlist = []
    with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
        with pytest.raises(SystemExit):
            cli.arg_parse(*PROG_AND_VERSION)


@patch('sys.stderr')
def test_arg_parse_conflict_initial_run_and_watchlist_empty_run(argument_parser_class):
    argument_parser = argument_parser_class()
    argument_parser.initial_run = True
    argument_parser.watchlist = ['FOO']
    argument_parser.run = []
    with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
        with pytest.raises(SystemExit):
            cli.arg_parse(*PROG_AND_VERSION)
