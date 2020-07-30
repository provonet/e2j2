import unittest
import requests_mock
from dns.resolver import Resolver, NXDOMAIN, Timeout
from requests.exceptions import RequestException
from mock import patch, mock_open, MagicMock
from consul.base import ACLPermissionDenied
from e2j2.tags import base64_tag, consul_tag, file_tag, json_tag, jsonfile_tag, vault_tag, dns_tag, escape_tag
from e2j2.tags import list_tag as list_tag
from e2j2.exceptions import E2j2Exception

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
        with self.assertRaisesRegex(E2j2Exception, 'invalid JSON'):
            json_tag.parse('<invalid>')

    def test_parse_json_file(self):
        with patch('builtins.open'):
            with patch('e2j2.tags.jsonfile_tag.json.load', return_value={'foo': 'bar'}):
                self.assertEqual(jsonfile_tag.parse('myfile'), {'foo': 'bar'})

        with patch('builtins.open') as open_mock:
            open_mock.side_effect = IOError()
            with self.assertRaisesRegex(E2j2Exception, 'IOError raised while reading file'):
                jsonfile_tag.parse('myfile')

        with patch('builtins.open'):
            with patch('e2j2.tags.jsonfile_tag.json.load') as jsonload_mock:
                jsonload_mock.side_effect = JSONDecodeError('', '', 0)
                with self.assertRaisesRegex(E2j2Exception, 'invalid JSON'):
                    jsonfile_tag.parse('myfile')

    def test_base64(self):
        self.assertEqual(base64_tag.parse('Zm9vYmFy'), 'foobar')

        # TypeError
        with self.assertRaisesRegex(E2j2Exception, 'invalid BASE64 string'):
            base64_tag.parse(123456)

        # binascii.Error
        with self.assertRaisesRegex(E2j2Exception, 'invalid BASE64 string'):
            base64_tag.parse('123456')

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

        # permission denied
        consul_kv.get = MagicMock(side_effect = ACLPermissionDenied)
        with patch('e2j2.tags.consul_tag.ConsulKV', return_value=consul_kv):
            with self.assertRaisesRegex(E2j2Exception, '^access denied connecting to:'):
                consul_tag.parse(config, 'foo/bar')

        # key not found
        consul_kv.get = MagicMock(return_value=[])
        with patch('e2j2.tags.consul_tag.ConsulKV', return_value=consul_kv):
            with self.assertRaisesRegex(E2j2Exception, 'key not found'):
                consul_tag.parse(config, 'foo/bar')

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
            with self.assertRaisesRegex(E2j2Exception, 'IOError raised while reading file'):
                file_tag.parse('file.txt')

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
            with self.assertRaisesRegex(E2j2Exception, 'Path not found'):
                _ = vault.get_raw('kv1/secret')

        # access denied
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=403)
            with self.assertRaisesRegex(E2j2Exception, 'Forbidden'):
                _ = vault.get_raw('kv1/secret')

        # unexpected status_code
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=999)
            with self.assertRaisesRegex(E2j2Exception, ''):
                _ = vault.get_raw('kv1/secret')

        # request exception raised
        with patch('e2j2.tags.vault_tag.requests.get', side_effect=RequestException):
            with self.assertRaisesRegex(E2j2Exception, '^failed to connect to.+'):
                _ = vault.get_raw('kv1/secret')

        # k/v backend version 1
        vault = vault_tag.Vault(config={'url': 'https://localhost:8200', 'backend': 'kv1'})
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=200)
            response = vault.get_kv1('kv1/secret')
            self.assertEqual(response, {'foo': 'bar'})

        # not found
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv1/secret', json=raw_response_v1, status_code=404)
            with self.assertRaisesRegex(E2j2Exception, 'Path not found'):
                _ = vault.get_kv1('kv1/secret')

        vault.get_raw = MagicMock(return_value='error')
        self.assertEqual(vault.get_kv1('kv1/secret'), 'error')

        # k/v backend version 2
        vault = vault_tag.Vault(config={'url': 'https://localhost:8200', 'backend': 'kv2'})
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv2/data/secret', json=raw_response_v2, status_code=200)
            response = vault.get_kv2('kv2/secret')
            self.assertEqual(response, {'foo': 'bar'})

        # k/v backend version 2
        with requests_mock.mock() as req_mock:
            req_mock.get('https://localhost:8200/v1/kv2/data/secret', json=raw_response_v2, status_code=404)
            with self.assertRaisesRegex(E2j2Exception, 'Path not found'):
                _ = vault.get_kv2('kv2/secret')

        vault.get_raw = MagicMock(return_value='error')
        self.assertEqual(vault.get_kv2('kv2/secret'), 'error')

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
        with self.assertRaisesRegex(E2j2Exception, 'Unknown K/V backend'):
            _ = vault_tag.parse(config, 'kv2/secret')

    def test_dns(self):
        resolver = Resolver()

        class Reply:
            pass

        # rdtype not set
        reply = Reply()
        reply.address = '127.0.0.1'
        resolver.query = MagicMock(return_value=[reply])
        with patch('e2j2.tags.dns_tag.Resolver', return_value=resolver):
            self.assertEqual(dns_tag.parse({}, 'www.foo.bar'), [{'address': '127.0.0.1'}])

        # rdtype set to 'A'
        reply = Reply()
        reply.address = '127.0.0.1'
        resolver.query = MagicMock(return_value=[reply])
        with patch('e2j2.tags.dns_tag.Resolver', return_value=resolver):
            self.assertEqual(dns_tag.parse({'type': 'A'}, 'www.foo.bar'), [{'address': '127.0.0.1'}])

        # rdtype set to 'AAAA'
        reply = Reply()
        reply.address = '::1'
        resolver.query = MagicMock(return_value=[reply])
        with patch('e2j2.tags.dns_tag.Resolver', return_value=resolver):
            self.assertEqual(dns_tag.parse({'type': 'AAAA'}, 'www.foo.bar'), [{'address': '::1'}])

        # rdtype set to 'SRV'
        reply = Reply()
        reply.target = 'srv1.foo.bar'
        reply.priority = 1
        reply.weight = 1
        reply.port = 123
        resolver.query = MagicMock(return_value=[reply])
        with patch('e2j2.tags.dns_tag.Resolver', return_value=resolver):
            self.assertEqual(dns_tag.parse({'type': 'SRV'}, 'srv.foo.bar'),
                             [{'target': 'srv1.foo.bar', 'priority': 1, 'weight': 1, 'port': 123}])

        # raise NXDOMAIN
        reply = Reply()
        resolver.query = MagicMock(side_effect=NXDOMAIN)
        with patch('e2j2.tags.dns_tag.Resolver', return_value=resolver):
            with self.assertRaisesRegex(E2j2Exception, 'The DNS query name does not exist'):
                dns_tag.parse({}, 'unknown.foo.bar')

        # raise Timeout
        reply = Reply()
        resolver.query = MagicMock(side_effect=Timeout)
        with patch('e2j2.tags.dns_tag.Resolver', return_value=resolver):
            with self.assertRaisesRegex(E2j2Exception, 'The DNS operation timed out'):
                dns_tag.parse({}, 'unknown.foo.bar')

        # raise other exception
        reply = Reply()
        resolver.query = MagicMock(side_effect=Exception('error'))
        with patch('e2j2.tags.dns_tag.Resolver', return_value=resolver):
            with self.assertRaisesRegex(E2j2Exception, 'error'):
                dns_tag.parse({}, 'unknown.foo.bar')

    def test_escape(self):
        self.assertEqual(escape_tag.parse('file://foobar'), 'file://foobar')


if __name__ == '__main__':
    unittest.main()
