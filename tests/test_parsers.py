import unittest
from mock import patch
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

    def test_parse64(self):
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

