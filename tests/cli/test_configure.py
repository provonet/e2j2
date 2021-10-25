import pytest
from mock import patch, mock_open
from e2j2 import cli
from e2j2.exceptions import E2j2Exception


class ArgumentParser:
    def __init__(self):
        self.filelist = []
        self.searchlist = None
        self.recursive = False
        self.ext = '.j2'
        self.no_color = True
        self.twopass = False
        self.nested_tags = False
        self.block_start = '{%'
        self.block_end = '%}'
        self.variable_start = '{{'
        self.variable_end = '}}'
        self.comment_start = '{#'
        self.comment_end = '#}'
        self.env_whitelist = None
        self.env_blacklist = None
        self.copy_file_permissions = False
        self.stacktrace = False
        self.config = None
        self.watchlist = None
        self.run = None
        self.noop = False
        self.splay = 0
        self.initial_run = False
        self.skip_render_on_undef = False
        self.marker_set = '{{'
        self.autodetect_marker_set = False
        self.stderr = False


@pytest.fixture
def args(argument_parser):
    return ArgumentParser()


def test_configure_read_config(args):
    args.config = 'config.json'
    open_mock = mock_open(read_data='{"searchlist": ["/foo"]}')
    with patch('e2j2.cli.open', open_mock):
        assert cli.configure(args)['searchlist'] == ['/foo']


def test_search_list(args):
    args.searchlist = '/path1,/path2'
    assert cli.configure(args)['searchlist'] == ['/path1', '/path2']

    args.searchlist = None
    with patch('os.environ.get', return_value='/path3,/path4'):
        assert cli.configure(args)['searchlist'] == ['/path3', '/path4']


def test_initial_run_required_params(args):
    args.initial_run = True

    # both set => should not raise an error
    args.watchlist = "foo,bar"
    args.run = ['/foobar.sh']
    assert cli.configure(args)

    # both unset => should raise an error
    args.watchlist = None
    args.run = None
    with pytest.raises(E2j2Exception):
        assert cli.configure(args)

    # watchlist set, run unset => should raise an error
    args.watchlist = "foo,bar"
    args.run = None
    with pytest.raises(E2j2Exception):
        assert cli.configure(args)

    # watchlist unset, run set => should raise an error
    args.watchlist = None
    args.run = '/foobar.sh'
    with pytest.raises(E2j2Exception):
        assert cli.configure(args)
