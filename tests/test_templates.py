import unittest
from mock import patch, mock_open
from unittest.mock import MagicMock
from e2j2.helpers import templates

class TestTemplates(unittest.TestCase):
    def setUp(self):
        pass

    def test_find(self):
        # recurse = True
        with patch('e2j2.helpers.templates.os.walk') as recurse_mock:
            templates.find(searchlist='/etc', j2file_ext='.j2', recurse=True)
            recurse_mock.assert_called_with('/etc')

        # recurse = False
        with patch('e2j2.helpers.templates.os.listdir') as dirlist_mock:
            templates.find(searchlist='/etc', j2file_ext='.j2', recurse=False)
            dirlist_mock.assert_called_with('/etc')

    def test_get_vars(self):
        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'FOO_ENV': 'json:{"key": "value"}'}
            self.assertEqual(templates.get_vars(), {})