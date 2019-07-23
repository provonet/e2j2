import unittest
import six
import requests_mock
from mock import patch, mock_open, MagicMock, mock
from consul.base import ACLPermissionDenied
from e2j2.tags import base64_tag, consul_tag, file_tag, json_tag, jsonfile_tag, vault_tag
from e2j2.tags import list_tag as list_tag

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class TestParsers(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_json(self):

        # render json string
        self.assertEqual(json_tag.parse('{"foo": "bar"}'), {'foo': 'bar'})

        # render json string with hash rockets
        self.assertEqual(json_tag.parse('{"foo"=>"bar"}'), {'foo': 'bar'})

        # invalid json
        self.assertEqual(json_tag.parse('<invalid>'), '** ERROR: Decoding JSON **')

    @unittest.skipIf(six.PY2, "not compatible with Python 2")
    def test_parse_json_file(self):
        with patch('builtins.open'):
            with patch('e2j2.tags.jsonfile_tag.json.load', return_value={'foo': 'bar'}):
                self.assertEqual(jsonfile_tag.parse('myfile'), {'foo': 'bar'})

        with patch('builtins.open') as open_mock:
            open_mock.side_effect = IOError()
            self.assertEqual(jsonfile_tag.parse('myfile'), '** ERROR: IOError raised while reading file **')

        with patch('builtins.open'):
            with patch('e2j2.tags.jsonfile_tag.json.load') as jsonload_mock:
                jsonload_mock.side_effect = JSONDecodeError('', '', 0)
                self.assertEqual(jsonfile_tag.parse('myfile'), '** Error: Decoding JSON **')

    def test_base64(self):
        self.assertEqual(base64_tag.parse('Zm9vYmFy'), 'foobar')

        # raise TypeError
        self.assertEqual(base64_tag.parse(123456), '** ERROR: decoding BASE64 string **')

        # raise binascii.Error
        self.assertEqual(base64_tag.parse('123456'), '** ERROR: decoding BASE64 string **')

    def test_consul(self):
        config = {'url': 'https://foobar', 'token': 'aabbccddee'}

        # test setup with config dict
        consul_kv = consul_tag.ConsulKV(config=config)
        self.assertEqual(consul_kv.scheme, 'https')
        self.assertEqual(consul_kv.host, 'foobar')
        self.assertEqual(consul_kv.port, 443)
        self.assertEqual(consul_kv.token, 'aabbccddee')

        # test setup with default values
        consul_kv = consul_tag.ConsulKV(config={})
        self.assertEqual(consul_kv.scheme, 'http')
        self.assertEqual(consul_kv.host, '127.0.0.1')
        self.assertEqual(consul_kv.port, 8500)
        self.assertEqual(consul_kv.token, None)

        # test get kv
        with patch.object(consul_kv.client.kv, 'get', return_value=(None, 'value')) as get_mock:
            consul_kv.get('foo/bar')
            get_mock.assert_called_with(key='foo/bar', recurse=False)

        # raise permission denied
        consul_kv.get = MagicMock(side_effect = ACLPermissionDenied)
        with patch('e2j2.tags.consul_tag.ConsulKV', return_value=consul_kv):
            self.assertEqual(consul_tag.parse(config, 'foo/bar'), '** Access denied connecting to: http://127.0.0.1:8500 **')

        # key not found
        consul_kv.get = MagicMock(return_value=[])
        with patch('e2j2.tags.consul_tag.ConsulKV', return_value=consul_kv):
            self.assertEqual(consul_tag.parse(config, 'foo/bar'), '** ERROR: Key not found **')

        # get nested consul entry
        value = [{'Key': 'key/folder/subkey', 'Value': 'foobar'}]
        consul_kv.get = MagicMock(return_value=value)
        with patch('e2j2.tags.consul_tag.ConsulKV', return_value=consul_kv):
            self.assertEqual(consul_tag.parse(config, 'key/folder/subkey'), 'foobar')

        # get consul entry
        value = [{'Key': 'key', 'Value': 'foobar'}]
        consul_kv.get = MagicMock(return_value=value)
        with patch('e2j2.tags.consul_tag.ConsulKV', return_value=consul_kv):
            self.assertEqual(consul_tag.parse(config, 'key'), 'foobar')

    def test_list(self):
        self.assertEqual(list_tag.parse('foo,bar'), ['foo', 'bar'])
        self.assertEqual(list_tag.parse('foo,  bar'), ['foo', 'bar'])
        self.assertNotEqual(list_tag.parse('foo|bar'), ['foo', 'bar'])

    def test_file(self):
        with patch('e2j2.tags.file_tag.open', mock_open(read_data='file content')):
            self.assertEqual(file_tag.parse('file.txt'), 'file content')

        open_mock = mock_open()
        open_mock.side_effect = IOError
        with patch('e2j2.tags.file_tag.open', open_mock):
            self.assertEqual(file_tag.parse('file.txt'), '** ERROR: IOError raised while reading file **')

    def test_vault(self):
        raw_response_v1 = {
            'request_id': 'd65c8fe2-ab82-8504-f700-16605a7f8fd0',
            'lease_id': '',
            'renewable': False,
            'lease_duration': 2764800,
            'data': {'foo': 'bar'},
            'wrap_info': None,
            'warnings': None,
            'auth': None
        }

        raw_response_v2 = {
            'request_id': '435d97f0-565e-164e-ffd1-45ee7bafc413',
            'lease_id': '',
            'renewable': False,
            'lease_duration': 0,
            'data': {
                'data': {
                    'foo': 'bar'
                },
                'metadata': {
                    'created_time': '2019-07-19T10:26:12.09232044Z',
                    'deletion_time': '',
                    'destroyed': False,
                    'version': 1
                }
            },
            'wrap_info': None,
            'warnings': None,
            'auth': None
        }

        config = {'url': 'https://localhost', 'token': 'aabbccddee'}

        # test setup with config dict
        vault = vault_tag.Vault(config=config)
        self.assertEqual(vault.scheme, 'https')
        self.assertEqual(vault.host, 'localhost')
        self.assertEqual(vault.port, 443)
        self.assertEqual(vault.token, 'aabbccddee')

        # test setup with default values
        vault = vault_tag.Vault(config={})
        self.assertEqual(vault.scheme, 'https')
        self.assertEqual(vault.host, '127.0.0.1')
        self.assertEqual(vault.port, 8200)
        self.assertEqual(vault.token, None)

        # test get_raw
        vault = vault_tag.Vault(config={'url': 'https://localhost:8200'})
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=200)
            response = vault.get_raw('kv1/secret')
            self.assertEqual(response, raw_response_v1)

        # not found
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=404)
            response = vault.get_raw('kv1/secret')
            self.assertEqual(response, '** ERROR: Invalid path **')

        # access denied
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=403)
            response = vault.get_raw('kv1/secret')
            self.assertEqual(response, '** ERROR: Forbidden **')

        # unexpected status_code
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=999)
            response = vault.get_raw('kv1/secret')
            self.assertEqual(response, '** ERROR: 999 **')

        # k/v backend version 1
        vault = vault_tag.Vault(config={'url': 'https://localhost:8200', 'backend': 'kv1'})
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=200)
            response = vault.get_kv1('kv1/secret')
            self.assertEqual(response, {'foo': 'bar'})

        # not found
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=404)
            response = vault.get_kv1('kv1/secret')
            self.assertEqual(response, '** ERROR: Invalid path **')

        # k/v backend version 2
        vault = vault_tag.Vault(config={'url': 'https://localhost:8200', 'backend': 'kv2'})
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv2/data/secret', json=raw_response_v2, status_code=200)
            response = vault.get_kv2('kv2/secret')
            self.assertEqual(response, {'foo': 'bar'})

        # k/v backend version 2
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv2/data/secret', json=raw_response_v2, status_code=404)
            response = vault.get_kv2('kv2/secret')
            self.assertEqual(response, '** ERROR: Invalid path **')

        # test parse no backend
        config = {'url': 'https://localhost:8200'}
        with patch('e2j2.tags.vault_tag.Vault.get_raw') as vault_mock:
            _ = vault_tag.parse(config, 'kv1/secret')
            vault_mock.assert_called_with('kv1/secret')

        # test parse k/v backend version 1
        config = {'url': 'https://localhost:8200', 'backend': 'kv1'}
        with patch('e2j2.tags.vault_tag.Vault.get_kv1') as vault_mock:
            _ = vault_tag.parse(config, 'kv1/secret')
            vault_mock.assert_called_with('kv1/secret')

        # test parse  k/v backend version 2
        config = {'url': 'https://localhost:8200', 'backend': 'kv2'}
        with patch('e2j2.tags.vault_tag.Vault.get_kv2') as vault_mock:
            _ = vault_tag.parse(config, 'kv2/secret')
            vault_mock.assert_called_with('kv2/secret')

        # test parse invalid backend
        config = {'url': 'https://localhost:8200', 'backend': 'invalid'}
        response = vault_tag.parse(config, 'kv2/secret')
        self.assertEqual(response, '** ERROR: Unknown backend **')


if __name__ == '__main__':
    unittest.main()
