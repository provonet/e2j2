import pytest
from mock import patch
from e2j2.templates import detect_markers
from e2j2.exceptions import E2j2Exception


CONFIG = {
    'marker_set': '{{',
    'autodetect_marker_set': True,
    'block_start': None,
    'block_end': None,
    'variable_start': None,
    'variable_end': None,
    'comment_start': None,
    'comment_end': None,
    'config_start': None,
    'config_end': None,
}

MARKERS = {
    'block_start': '{%',
    'block_end': '%}',
    'variable_start': '{{',
    'variable_end': '}}',
    'comment_start': '{#',
    'comment_end': '#}',
    'config_start': '{',
    'config_end': '}',
}

ALT_MARKERS = {
    'block_start': '<%',
    'block_end': '%>',
    'variable_start': '<=',
    'variable_end': '=>',
    'comment_start': '<#',
    'comment_end': '#>',
    'config_start': '<',
    'config_end': '>',
}


def test_detect_markers_no_template():
    assert detect_markers(CONFIG, content='just content') == MARKERS


def test_detect_markers_default_markers():
    assert detect_markers(CONFIG, content='{{ FOO }}') == MARKERS


def test_detect_markers_default_config_markers():
    assert detect_markers(CONFIG, content='config={"key": "value"}') == MARKERS


def test_detect_markers_alternative_markers():
    assert detect_markers(CONFIG, content='<= FOO =>') == ALT_MARKERS


def test_detect_markers_alternative_config_markers():
    assert detect_markers(CONFIG, content='config=<"key": "value">') == ALT_MARKERS
