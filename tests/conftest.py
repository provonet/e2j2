import pytest


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
def argument_parser_class():
    return ArgumentParser


@pytest.fixture
def argument_parser():
    return ArgumentParser()
