from mock import patch
from e2j2.templates import get_vars


@patch('e2j2.templates.detect_markers')
@patch('e2j2.templates.os')
def test_get_vars(os_mocker, detect_markers_mock):
    config = {'no_color': True, 'twopass': True, 'nested_tags': False}

    os_mocker.environ = {'FOO_ENV': 'json:{"key": "value"}'}
    assert get_vars(config, whitelist=['FOO_ENV'], blacklist=[]) == {'FOO_ENV': {'key': 'value'}}

    # whitelist / blacklist
    assert get_vars(config, whitelist=['FOO_ENV'], blacklist=['FOO_ENV']) == {}
