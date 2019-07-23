import unittest
from mock import patch
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
            self.assertEqual(templates.get_vars(whitelist=['FOO_ENV'], blacklist=[]), {'FOO_ENV': {'key': 'value'}})

        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'FOO_ENV': 'json:{"key": "value"}'}

            with patch('e2j2.helpers.templates.stdout'):
                with patch('e2j2.helpers.templates.parse_tag', return_value='** ERROR: Key not found **'):
                    self.assertEqual(templates.get_vars(whitelist=['FOO_ENV'], blacklist=[]), {'FOO_ENV': '** ERROR: Key not found **'})

        # whitelist / blacklist
        self.assertEqual(templates.get_vars(whitelist=['FOO_ENV'], blacklist=['FOO_ENV']), {})

    def test_render(self):
        with patch('e2j2.helpers.templates.jinja2.Environment') as jinja2_mock:

            # one pass
            jinja2_mock.return_value.get_template.return_value.render.return_value = 'rendered template'
            response = templates.render(
                        j2file='/foo/file1.j2',
                        twopass=False,
                        block_start='{%',
                        block_end='%}',
                        variable_start='{{',
                        variable_end='}}',
                        comment_start='{#',
                        comment_end='#}',
                        j2vars={"FOO": "BAR"})

            jinja2_mock.return_value.get_template.assert_called_with('file1.j2')
            jinja2_mock.return_value.get_template.return_value.render.assert_called_with({"FOO": "BAR"})
            self.assertEqual(response, 'rendered template')

            # two pass
            jinja2_mock.return_value.from_string.return_value.render.return_value = 'rendered template'
            response = templates.render(
                        j2file='/foo/file1.j2',
                        twopass=True,
                        block_start='{%',
                        block_end='%}',
                        variable_start='{{',
                        variable_end='}}',
                        comment_start='{#',
                        comment_end='#}',
                        j2vars={"FOO": "BAR"})

            jinja2_mock.return_value.from_string.assert_called_with('rendered template')
            jinja2_mock.return_value.from_string.return_value.render.assert_called_with({"FOO": "BAR"})
            self.assertEqual(response, 'rendered template')

    def test_parse_tag(self):
        with patch('e2j2.helpers.templates.json_tag.parse') as json_mock:
            templates.parse_tag('json:', '{}')
            json_mock.assert_called_with('{}')

        with patch('e2j2.helpers.templates.jsonfile_tag.parse') as jsonfile_mock:
            templates.parse_tag('jsonfile:', 'file.json')
            jsonfile_mock.assert_called_with('file.json')

        with patch('e2j2.helpers.templates.base64_tag.parse') as base64_mock:
            templates.parse_tag('base64:', 'Zm9vYmFy')
            base64_mock.assert_called_with('Zm9vYmFy')

        with patch('e2j2.helpers.templates.consul_tag.parse') as consul_mock:
            templates.parse_tag('consul:', 'consulkey')
            consul_mock.assert_called_with({}, 'consulkey')

        with patch('e2j2.helpers.templates.list_tag.parse') as list_mock:
            templates.parse_tag('list:', 'foo,bar')
            list_mock.assert_called_with('foo,bar')

        with patch('e2j2.helpers.templates.file_tag.parse') as file_mock:
            templates.parse_tag('file:', 'file.txt')
            file_mock.assert_called_with('file.txt')

        # no config
        with patch('e2j2.helpers.templates.vault_tag.parse') as vault_mock:
            templates.parse_tag('vault:', 'secret/mysecret')
            vault_mock.assert_called_with({}, 'secret/mysecret')

        # with config
        with patch('e2j2.helpers.templates.vault_tag.parse') as vault_mock:
            templates.parse_tag('vault:', 'config={"url": "https://localhost:8200"}:secret/mysecret')
            vault_mock.assert_called_with({"url": "https://localhost:8200"}, 'secret/mysecret')

        # with envar config
        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'VAULT_CONFIG': '{"url": "https://localhost:8200"}'}
            with patch('e2j2.helpers.templates.vault_tag.parse') as vault_mock:
                templates.parse_tag('vault:', 'secret/mysecret')
                vault_mock.assert_called_with({"url": "https://localhost:8200"}, 'secret/mysecret')

        # with envvar config and token envvar
        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'VAULT_CONFIG': '{"url": "https://localhost:8200"}', 'VAULT_TOKEN': 'aabbccddee'}
            with patch('e2j2.helpers.templates.vault_tag.parse') as vault_mock:
                templates.parse_tag('vault:', 'secret/mysecret')
                vault_mock.assert_called_with(
                    {'url': 'https://localhost:8200', 'token': 'aabbccddee'}, 'secret/mysecret')

        # schema validation error
        self.assertEqual(templates.parse_tag(
            'vault:', 'config={"invalid": "foobar"}:secret/mysecret'), '** ERROR: config validation failed **')

        # invalid json in config
        self.assertEqual(templates.parse_tag(
            'vault:', 'config={"<invalid>"}::secret/mysecret'), '** ERROR: Decoding JSON **')

        # unknown tag
        self.assertEqual(templates.parse_tag('unknown:', 'foobar'), '** ERROR: tag: unknown: not implemented **')


if __name__ == '__main__':
    unittest.main()
