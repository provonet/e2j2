import unittest
import six
from mock import patch, mock_open, MagicMock
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
        # raise JSonDecodeError

        with patch('e2j2.tags.consul_tag.os') as os_mock:
            os_mock.environ = {'CONSUL_CONFIG': '<INVALIDJSON>'}
            self.assertEqual(consul_tag.parse('foobar'), '** ERROR: parsing consul_config **')

        # test setup with config dict
        consul_kv = consul_tag.ConsulKV(config={'scheme': 'https', 'host': 'foobar', 'port': 443, 'token': 'aabbccddee'})
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
            self.assertEqual(consul_tag.parse('foo/bar'), '** Access denied connecting to: http://127.0.0.1:8500 **')

        # key not found
        consul_kv.get = MagicMock(return_value=[])
        with patch('e2j2.tags.consul_tag.ConsulKV', return_value=consul_kv):
            self.assertEqual(consul_tag.parse('foo/bar'), '** ERROR: Key not found **')

        # get nested consul entry
        value = [{'Key': 'key/folder/subkey', 'Value': 'foobar'}]
        consul_kv.get = MagicMock(return_value=value)
        with patch('e2j2.tags.consul_tag.ConsulKV', return_value=consul_kv):
            self.assertEqual(consul_tag.parse('key/folder/subkey'), 'foobar')

        # get consul entry
        value = [{'Key': 'key', 'Value': 'foobar'}]
        consul_kv.get = MagicMock(return_value=value)
        with patch('e2j2.tags.consul_tag.ConsulKV', return_value=consul_kv):
            self.assertEqual(consul_tag.parse('key'), 'foobar')

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


if __name__ == '__main__':
    unittest.main()
