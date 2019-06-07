import unittest
import six
from mock import patch, mock_open, MagicMock
from consul.base import ACLPermissionDenied
from e2j2.helpers import parsers

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class TestParsers(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_json_string(self):

        # render json string
        self.assertEqual(parsers.parse_json_string('{"foo": "bar"}'), {'foo': 'bar'})

        # render json string with hash rockets
        self.assertEqual(parsers.parse_json_string('{"foo"=>"bar"}'), {'foo': 'bar'})

        # invalid json
        self.assertEqual(parsers.parse_json_string('<invalid>'), '** ERROR: Decoding JSON **')

    @unittest.skipIf(six.PY2, "not compatible with Python 2")
    def test_parse_json_file(self):
        with patch('builtins.open'):
            with patch('e2j2.helpers.parsers.json.load', return_value={'foo': 'bar'}):
                self.assertEqual(parsers.parse_json_file('myfile'), {'foo': 'bar'})

        with patch('builtins.open') as open_mock:
            open_mock.side_effect = IOError()
            self.assertEqual(parsers.parse_json_file('myfile'), '** ERROR: IOError raised while reading file **')

        with patch('builtins.open'):
            with patch('e2j2.helpers.parsers.json.load') as jsonload_mock:
                jsonload_mock.side_effect = JSONDecodeError('', '', 0)
                self.assertEqual(parsers.parse_json_file('myfile'), '** Error: Decoding JSON **')

    def test_base64(self):
        self.assertEqual(parsers.parse_base64('Zm9vYmFy'), 'foobar')

        # raise TypeError
        self.assertEqual(parsers.parse_base64(123456), '** ERROR: decoding BASE64 string **')

        # raise binascii.Error
        self.assertEqual(parsers.parse_base64('123456'), '** ERROR: decoding BASE64 string **')

    def test_consul(self):
        # raise JSonDecodeError

        with patch('e2j2.helpers.parsers.os') as os_mock:
            os_mock.environ = {'CONSUL_CONFIG': '<INVALIDJSON>'}
            self.assertEqual(parsers.parse_consul('foobar'), '** ERROR: parsing consul_config **')

        # test setup with config dict
        consul_kv = parsers.ConsulKV(config={'scheme': 'https', 'host': 'foobar', 'port': 443, 'token': 'aabbccddee'})
        self.assertEqual(consul_kv.scheme, 'https')
        self.assertEqual(consul_kv.host, 'foobar')
        self.assertEqual(consul_kv.port, 443)
        self.assertEqual(consul_kv.token, 'aabbccddee')

        # test setup with default values
        consul_kv = parsers.ConsulKV(config={})
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
        with patch('e2j2.helpers.parsers.ConsulKV', return_value=consul_kv):
            self.assertEqual(parsers.parse_consul('foo/bar'), '** Access denied connecting to: http://127.0.0.1:8500 **')

        # key not found
        consul_kv.get = MagicMock(return_value=[])
        with patch('e2j2.helpers.parsers.ConsulKV', return_value=consul_kv):
            self.assertEqual(parsers.parse_consul('foo/bar'), '** ERROR: Key not found **')

        # get nested consul entry
        value = [{'Key': 'key/folder/subkey', 'Value': 'foobar'}]
        consul_kv.get = MagicMock(return_value=value)
        with patch('e2j2.helpers.parsers.ConsulKV', return_value=consul_kv):
            self.assertEqual(parsers.parse_consul('key/folder/subkey'), 'foobar')

        # get consul entry
        value = [{'Key': 'key', 'Value': 'foobar'}]
        consul_kv.get = MagicMock(return_value=value)
        with patch('e2j2.helpers.parsers.ConsulKV', return_value=consul_kv):
            self.assertEqual(parsers.parse_consul('key'), 'foobar')

    def test_list(self):
        self.assertEqual(parsers.parse_list('foo,bar'), ['foo', 'bar'])
        self.assertEqual(parsers.parse_list('foo,  bar'), ['foo', 'bar'])
        self.assertNotEqual(parsers.parse_list('foo|bar'), ['foo', 'bar'])

    def test_file(self):
        with patch('e2j2.helpers.parsers.open', mock_open(read_data='file content')):
            self.assertEqual(parsers.parse_file('file.txt'), 'file content')

        open_mock = mock_open()
        open_mock.side_effect = IOError
        with patch('e2j2.helpers.parsers.open', open_mock):
            self.assertEqual(parsers.parse_file('file.txt'), '** ERROR: IOError raised while reading file **')

    def test_parse_tag(self):
        with patch('e2j2.helpers.parsers.parse_json_string') as json_mock:
            parsers.parse_tag('json:', '{}')
            json_mock.assert_called_with('{}')

        with patch('e2j2.helpers.parsers.parse_json_file') as jsonfile_mock:
            parsers.parse_tag('jsonfile:', 'file.json')
            jsonfile_mock.assert_called_with('file.json')

        with patch('e2j2.helpers.parsers.parse_base64') as base64_mock:
            parsers.parse_tag('base64:', 'Zm9vYmFy')
            base64_mock.assert_called_with('Zm9vYmFy')

        with patch('e2j2.helpers.parsers.parse_consul') as consul_mock:
            parsers.parse_tag('consul:', 'consulkey')
            consul_mock.assert_called_with('consulkey')

        with patch('e2j2.helpers.parsers.parse_list') as list_mock:
            parsers.parse_tag('list:', 'foo,bar')
            list_mock.assert_called_with('foo,bar')

        with patch('e2j2.helpers.parsers.parse_file') as file_mock:
            parsers.parse_tag('file:', 'file.txt')
            file_mock.assert_called_with('file.txt')

        self.assertEqual(parsers.parse_tag('unknown:', 'foobar'), '** ERROR: tag: unknown: not implemented **')


if __name__ == '__main__':
    unittest.main()
