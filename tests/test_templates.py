import unittest
import traceback
from mock import patch, MagicMock, call
from callee import Contains
from six import assertRaisesRegex, PY2
from e2j2.helpers import templates
from e2j2.helpers.exceptions import E2j2Exception
from jinja2.exceptions import TemplateNotFound, UndefinedError, FilterArgumentError, TemplateSyntaxError


class TestTemplates(unittest.TestCase):
    def setUp(self):
        pass

    def test_find(self):
        # recurse = True
        with patch('e2j2.helpers.templates.os.walk') as recurse_mock:
            templates.find(searchlist=['/etc'], j2file_ext='.j2', recurse=True)
            recurse_mock.assert_called_with('/etc')

        # recurse = False
        with patch('e2j2.helpers.templates.os.listdir') as dirlist_mock:
            templates.find(searchlist=['/etc'], j2file_ext='.j2', recurse=False)
            dirlist_mock.assert_called_with('/etc')

    def test_get_vars(self):
        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'FOO_ENV': 'json:{"key": "value"}'}
            self.assertEqual(templates.get_vars(whitelist=['FOO_ENV'], blacklist=[]), {'FOO_ENV': {'key': 'value'}})

        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'FOO_ENV': 'json:{"key": "value"}'}

            with patch('e2j2.helpers.templates.parse_tag', side_effect=E2j2Exception('foobar error')):
                with patch('e2j2.helpers.templates.stdout') as stdout_mock:
                    templates.get_vars(whitelist=['FOO_ENV'], blacklist=[])
                    stdout_mock.assert_called_with(Contains('foobar error'))

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

        class J2:
            pass

        class Template:
            pass

        j2 = J2()
        template = Template()

        # exception should contain line number
        exceptions = [
            UndefinedError(),
            FilterArgumentError(),
            TemplateSyntaxError(message='message', lineno=1),
        ]
        for exception in exceptions:
            template.render = MagicMock(side_effect=exception)
            j2.get_template = MagicMock(return_value=template)
            with patch('e2j2.helpers.templates.jinja2.Environment', return_value=j2):
                with assertRaisesRegex(self, E2j2Exception, 'at line'):
                    _ = templates.render(
                        j2file='/foo/file1.j2',
                        twopass=False,
                        block_start='{%',
                        block_end='%}',
                        variable_start='{{',
                        variable_end='}}',
                        comment_start='{#',
                        comment_end='#}',
                        j2vars={"FOO": "BAR"})

        # template not found exception
        template.render = MagicMock(side_effect=TemplateNotFound(name='/foo/file1.j2'))
        j2.get_template = MagicMock(return_value=template)
        with patch('e2j2.helpers.templates.jinja2.Environment', return_value=j2):
            with assertRaisesRegex(self, E2j2Exception, 'Template file1.j2 not found'):
                _ = templates.render(
                    j2file='/foo/file1.j2',
                    twopass=False,
                    block_start='{%',
                    block_end='%}',
                    variable_start='{{',
                    variable_end='}}',
                    comment_start='{#',
                    comment_end='#}',
                    j2vars={"FOO": "BAR"})

        # other exceptions
        template.render = MagicMock(side_effect=ValueError('Error'))
        j2.get_template = MagicMock(return_value=template)
        with patch('e2j2.helpers.templates.jinja2.Environment', return_value=j2):
            with assertRaisesRegex(self, E2j2Exception, 'Error'):
                _ = templates.render(
                    j2file='/foo/file1.j2',
                    twopass=False,
                    block_start='{%',
                    block_end='%}',
                    variable_start='{{',
                    variable_end='}}',
                    comment_start='{#',
                    comment_end='#}',
                    j2vars={"FOO": "BAR"})

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

        with patch('e2j2.helpers.templates.dns_tag.parse') as dns_mock:
            templates.parse_tag('dns:', 'config={"type": "MX"}:mx.foo.bar')
            dns_mock.assert_called_with({'type': 'MX'}, 'mx.foo.bar')

        # with config
        with patch('e2j2.helpers.templates.dns_tag.parse') as dns_mock:
            templates.parse_tag('dns:', 'www.foo.bar')
            dns_mock.assert_called_with({}, 'www.foo.bar')

        # schema validation error including stacktrace
        with patch('e2j2.helpers.templates.cache') as cache_mock:
            with patch('e2j2.helpers.templates.stdout') as stdout_mock:
                cache_mock.config = {'stacktrace': True}
                try:
                    templates.parse_tag('vault:', 'config={"invalid": "foobar"}:secret/mysecret')
                except E2j2Exception as error:
                    self.assertEqual(str(error), 'config validation failed')
                    stdout_mock.assert_called_with(Contains('Traceback'))

        # invalid json in config
        try:
            templates.parse_tag('vault:', 'config={"<invalid>"}::secret/mysecret')
        except E2j2Exception as error:
            self.assertEqual(str(error), 'decoding JSON failed')

        # unknown tag
        self.assertEqual(templates.parse_tag('unknown:', 'foobar'), '** ERROR: tag: unknown: not implemented **')

    @unittest.skipIf(PY2, "not compatible with Python 2")
    def test_stdout(self):
        with patch('e2j2.helpers.templates.sys.stdout.write') as stdout_mock:
            templates.stdout('foobar')
            stdout_mock.assert_called_with('foobar')

        with patch('e2j2.helpers.templates.sys.stdout.write') as stdout_mock:
            with patch('e2j2.helpers.templates.cache') as cache_mock:
                cache_mock.log_repeat_log_msg_counter = 1
                cache_mock.log_display_every = 2
                templates.stdout('foobar')
                templates.stdout('foobar')
                stdout_mock.assert_has_calls([call('foobar'), call('(2x) foobar')])


if __name__ == '__main__':
    unittest.main()
