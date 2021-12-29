import pytest
from mock import patch
from e2j2.templates import parse_tag
from e2j2.exceptions import E2j2Exception

@patch('e2j2.templates.json_tag.parse')
def test_parse_tag_json(json_mocker, config):
    parse_tag(config, 'json:', 'json:{}')
    json_mocker.assert_called_with('{}')


@patch('e2j2.templates.jsonfile_tag.parse')
def test_parse_tag_jsonfile(jsonfile_mocker, config):
    parse_tag(config, 'jsonfile:', 'jsonfile:file.json')
    jsonfile_mocker.assert_called_with('file.json')


@patch('e2j2.templates.base64_tag.parse')
def test_parse_tag_base64(base64_mocker, config):
    parse_tag(config, 'base64:', 'base64:Zm9vYmFy')
    base64_mocker.assert_called_with('Zm9vYmFy')


@patch('e2j2.templates.consul_tag.parse')
def test_parse_tag_consul(consul_mocker, config):
    parse_tag(config, 'consul:', 'consul:path/key')
    consul_mocker.assert_called_with({}, 'path/key')


@patch('e2j2.templates.list_tag.parse')
def test_parse_tag_list(list_mocker, config):
    parse_tag(config, 'list:', 'list:foo,bar')
    list_mocker.assert_called_with('foo,bar')


@patch('e2j2.templates.file_tag.parse')
def test_parse_tag_file(file_mocker, config):
    parse_tag(config, 'file:', 'file:file.json')
    file_mocker.assert_called_with('file.json')


@patch('e2j2.templates.vault_tag.parse')
def test_parse_tag_vault(vault_mocker, config):
    parse_tag(config, 'vault:', 'vault:secret/mysecret')
    vault_mocker.assert_called_with({}, 'secret/mysecret')


@patch('e2j2.templates.escape_tag.parse')
def test_parse_tag_escape(escape_mocker, config):
    parse_tag(config, 'escape:', 'file:foobar')
    escape_mocker.assert_called_with('file:foobar')


@patch('e2j2.templates.dns_tag.parse')
def test_parse_tag_dns(dns_mocker, config):
    parse_tag(config, 'dns:', 'dns:node1.node.consul')
    dns_mocker.assert_called_with({}, 'node1.node.consul')


@patch('e2j2.templates.dns_tag.parse')
def test_parse_tag_dns(dns_mocker, config):
    parse_tag(config, 'dns:', 'dns:config={"type": "SRV"}:_my-service._tcp.service.consul')
    dns_mocker.assert_called_with({'type': 'SRV'}, '_my-service._tcp.service.consul')


@patch('e2j2.templates.vault_tag.parse')
def test_parse_tag_vault_with_config(vault_mocker, config):
    parse_tag(config, 'vault:', 'vault:config={"url": "https://localhost:8200"}:secret/mysecret')
    vault_mocker.assert_called_with({"url": "https://localhost:8200"}, 'secret/mysecret')


@patch('e2j2.templates.vault_tag.parse')
def test_parse_tag_vault_with_config_and_alternative_markers(vault_mocker, config):
    config['config_start'] = '['
    config['config_end'] = ']'
    parse_tag(config, 'vault:', 'vault:config=["url": "https://localhost:8200"]:secret/mysecret')
    vault_mocker.assert_called_with({"url": "https://localhost:8200"}, 'secret/mysecret')


@patch('e2j2.templates.vault_tag.parse')
@patch('e2j2.templates.os')
def test_parse_tag_vault_with_config_from_envar(os_mocker, vault_mocker, config):
    os_mocker.environ = {'VAULT_CONFIG': '{"url": "https://localhost:8200"}', 'VAULT_TOKEN': 'aabbccddee'}
    parse_tag(config, 'vault:', 'vault:secret/mysecret')
    vault_mocker.assert_called_with({'url': 'https://localhost:8200', 'token': 'aabbccddee'}, 'secret/mysecret')


@patch('e2j2.templates.file_tag.parse', return_value='aabbccddee')
@patch('e2j2.templates.vault_tag.parse')
def test_vault_tag_read_token_from_file(vault_mocker, _, config):
    parse_tag(config, 'vault:', 'vault:config={"url": "https://localhost:8200", "token": "file:/tmp/myfile"}:secret/mysecret')
    vault_mocker.assert_called_with(
        {'url': 'https://localhost:8200', 'token': 'aabbccddee'}, 'secret/mysecret'
    )


@patch('e2j2.templates.write')
def test_vault_tag_failed_validation(display_mock, config):
    config['stacktrace'] = True
    with pytest.raises(E2j2Exception) as err:
        parse_tag(config, 'vault:', 'config={"invalid": "foobar"}:secret/mysecret')

    assert 'config validation failed' in str(err)
    assert "Traceback" in display_mock.call_args[0][0]


def test_vault_tag_invalid_json(config):
    with pytest.raises(E2j2Exception) as err:
        parse_tag(config, 'vault:', 'config={"<invalid>"}::secret/mysecret')

    assert 'decoding JSON failed' in str(err)


def test_unknown_tag(config):
    assert parse_tag(config, 'unknown:', 'foobar') == (None, '** ERROR: tag: unknown: not implemented **')


def test_wrong_markers(config):
    with pytest.raises(E2j2Exception) as err:
        parse_tag(config, "dns:", 'dns:config=|"type": "SRV"')

    assert 'invalid config markers used' in str(err)
