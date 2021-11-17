import pytest
from mock import patch
from e2j2.exceptions import E2j2Exception
from e2j2 import templates


MARKERS = {
    "block_start": "{%",
    "block_end": "%}",
    "variable_start": "{{",
    "variable_end": "}}",
    "comment_start": "{#",
    "comment_end": "#}",
    "config_start": "{",
    "config_end": "}",
}


@pytest.fixture(autouse=True)
def display_mocker():
    with patch("e2j2.templates.write") as mocker:
        yield mocker


@pytest.fixture(autouse=True)
def detect_marker():
    with patch("e2j2.templates.detect_markers") as mocker:
        mocker.return_value = MARKERS
        yield mocker


def test_resolv_vars():
    config = {"no_color": True, "nested_tags": False}
    assert (
        templates.resolv_vars(
            config,
            var_list=["FOO_ENV"],
            env_vars={"FOO_ENV": 'json:{"key": "base64:dmFsdWU="}'},
        )
        == {"FOO_ENV": {"key": "base64:dmFsdWU="}}
    )


def test_resolv_vars_nested():
    config = {"no_color": True, "nested_tags": True}

    # fmt: off
    assert (
        templates.resolv_vars(
            config,
            var_list=["FOO_ENV"],
            env_vars={"FOO_ENV": 'json:{"key": "base64:dmFsdWU="}'},
        ) == {"FOO_ENV": {"key": "value"}}
    )
    # fmt: on


@patch("e2j2.templates.parse_tag")
def test_resolv_vars_error(parse_tag_mocker, display_mocker):
    config = {"no_color": True, "nested_tags": False}
    parse_tag_mocker.side_effect = E2j2Exception("foobar error")
    templates.resolv_vars(
        config, var_list=["FOO_ENV"], env_vars={"FOO_ENV": 'json:{"key": "value"}'}
    )
    mock_args = display_mocker.call_args
    assert "failed with error: foobar error" in mock_args[0][0]


@patch("e2j2.templates.file_tag.parse")
def test_resolv_vars_nested_error(filetag_mocker, display_mocker):
    config = {"no_color": True, "nested_tags": True}

    filetag_mocker.side_effect = E2j2Exception(
        "IOError raised while reading file: /foobar.txt"
    )

    templates.resolv_vars(
        config,
        var_list=["FOO_ENV"],
        env_vars={"FOO_ENV": 'json:{"key": "file:/foobar.txt"}'},
    )

    mock_args = display_mocker.call_args
    assert "failed to resolve nested tag" in mock_args[0][0]


def test_resolv_vars_string():
    config = {"no_color": True, "nested_tags": False}

    assert templates.resolv_vars(
        config, var_list=["FOO_ENV"], env_vars={"FOO_ENV": 'json:{"key": "value"}'}
    ) == {"FOO_ENV": {"key": "value"}}


def test_resolv_vars_boolean():
    config = {"no_color": True, "nested_tags": False}

    assert templates.resolv_vars(
        config, var_list=["FOO_ENV"], env_vars={"FOO_ENV": 'json:{"key": true}'}
    ) == {"FOO_ENV": {"key": True}}


def test_resolv_vars_int():
    config = {"no_color": True, "nested_tags": False}

    assert templates.resolv_vars(
        config, var_list=["FOO_ENV"], env_vars={"FOO_ENV": 'json:{"key": 1}'}
    ) == {"FOO_ENV": {"key": 1}}


def test_resolv_vars_flatten():
    config = {"no_color": True, "nested_tags": False}

    # test with config flatten=True return value from call should return a dict with a foobar key
    assert "foobar" in templates.resolv_vars(
        config,
        var_list=["FOO_ENV"],
        env_vars={
            "FOO_ENV": 'json:config={"flatten": true}:{"foobar": "foobar_value"}'
        },
    )


def test_resolv_vars_unflatten():
    config = {"no_color": True, "nested_tags": False}

    # test with config flatten=False return value from call should not have a foobar key
    assert "foobar" not in templates.resolv_vars(
        config,
        var_list=["FOO_ENV"],
        env_vars={
            "FOO_ENV": 'json:config={"flatten": false}:{"foobar": "foobar_value"}'
        },
    )
