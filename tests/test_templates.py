import unittest
from mock import patch, MagicMock, call
from callee import Contains
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
            recurse_mock.assert_called_with('/etc', followlinks=True)

        # recurse = False
        with patch('e2j2.helpers.templates.os.listdir') as dirlist_mock:
            templates.find(searchlist=['/etc'], j2file_ext='.j2', recurse=False)
            dirlist_mock.assert_called_with('/etc')

    def test_recursive_iter(self):
        # flat dict
        data = {'test_key', 'test_value'}
        self.assertEqual(list(templates.recursive_iter(data)), [((), {'test_key', 'test_value'})])

        # nested dict
        data = {'nestedkey': {'test_key', 'test_value'}}
        self.assertEqual(list(templates.recursive_iter(data)), [(('nestedkey',), {'test_key', 'test_value'})])

        # list of dict
        data = {'listofdict': [{'test_key', 'test_value'}]}
        self.assertEqual(list(templates.recursive_iter(data)), [(('listofdict',0), {'test_key', 'test_value'})])

    def test_get_vars(self):
        config = {'no_color': True, 'twopass': True}

        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'FOO_ENV': 'json:{"key": "value"}'}
            self.assertEqual(templates.get_vars(config, whitelist=['FOO_ENV'], blacklist=[]), {'FOO_ENV': {'key': 'value'}})

            # whitelist / blacklist
            self.assertEqual(templates.get_vars(config, whitelist=['FOO_ENV'], blacklist=['FOO_ENV']), {})

    def test_resolv_vars(self):
        config = {'no_color': True, 'twopass': True}
        with patch('e2j2.helpers.templates.os') as os_mock:

            with patch('e2j2.helpers.templates.parse_tag', side_effect=E2j2Exception('foobar error')):
                with patch('e2j2.helpers.templates.stdout') as stdout_mock:
                    templates.resolv_vars(config, var_list=['FOO_ENV'], vars={'FOO_ENV': 'json:{"key": "value"}'})
                    stdout_mock.assert_called_with(Contains('foobar error'))


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
                with self.assertRaisesRegex(E2j2Exception, 'at line'):
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
            with self.assertRaisesRegex(E2j2Exception, 'Template file1.j2 not found'):
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
            with self.assertRaisesRegex(E2j2Exception, 'Error'):
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
        config = {'stacktrace': True, 'no_color': True, 'twopass': True}

        with patch('e2j2.helpers.templates.json_tag.parse') as json_mock:
            templates.parse_tag(config, 'json:', '{}')
            json_mock.assert_called_with('{}')

        with patch('e2j2.helpers.templates.jsonfile_tag.parse') as jsonfile_mock:
            templates.parse_tag(config, 'jsonfile:', 'file.json')
            jsonfile_mock.assert_called_with('file.json')

        with patch('e2j2.helpers.templates.base64_tag.parse') as base64_mock:
            templates.parse_tag(config, 'base64:', 'Zm9vYmFy')
            base64_mock.assert_called_with('Zm9vYmFy')

        with patch('e2j2.helpers.templates.consul_tag.parse') as consul_mock:
            templates.parse_tag(config, 'consul:', 'consulkey')
            consul_mock.assert_called_with({}, 'consulkey')

        with patch('e2j2.helpers.templates.list_tag.parse') as list_mock:
            templates.parse_tag(config, 'list:', 'foo,bar')
            list_mock.assert_called_with('foo,bar')

        with patch('e2j2.helpers.templates.file_tag.parse') as file_mock:
            templates.parse_tag(config, 'file:', 'file.txt')
            file_mock.assert_called_with('file.txt')

        # no config
        with patch('e2j2.helpers.templates.vault_tag.parse') as vault_mock:
            templates.parse_tag(config, 'vault:', 'secret/mysecret')
            vault_mock.assert_called_with({}, 'secret/mysecret')

        # with config
        with patch('e2j2.helpers.templates.vault_tag.parse') as vault_mock:
            templates.parse_tag(config, 'vault:', 'config={"url": "https://localhost:8200"}:secret/mysecret')
            vault_mock.assert_called_with({"url": "https://localhost:8200"}, 'secret/mysecret')

        # with envar config
        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'VAULT_CONFIG': '{"url": "https://localhost:8200"}'}
            with patch('e2j2.helpers.templates.vault_tag.parse') as vault_mock:
                templates.parse_tag(config, 'vault:', 'secret/mysecret')
                vault_mock.assert_called_with({"url": "https://localhost:8200"}, 'secret/mysecret')

        # with envvar config and token envvar
        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'VAULT_CONFIG': '{"url": "https://localhost:8200"}', 'VAULT_TOKEN': 'aabbccddee'}
            with patch('e2j2.helpers.templates.vault_tag.parse') as vault_mock:
                templates.parse_tag(config, 'vault:', 'secret/mysecret')
                vault_mock.assert_called_with({'url': 'https://localhost:8200', 'token': 'aabbccddee'},
                                              'secret/mysecret')

        with patch('e2j2.helpers.templates.dns_tag.parse') as dns_mock:
            templates.parse_tag(config, 'dns:', 'config={"type": "MX"}:mx.foo.bar')
            dns_mock.assert_called_with({'type': 'MX'}, 'mx.foo.bar')

        # with config
        with patch('e2j2.helpers.templates.dns_tag.parse') as dns_mock:
            templates.parse_tag(config, 'dns:', 'www.foo.bar')
            dns_mock.assert_called_with({}, 'www.foo.bar')

        # schema validation error including stacktrace
        with patch('e2j2.helpers.templates.cache') as cache_mock:
            with patch('e2j2.helpers.templates.stdout') as stdout_mock:
                cache_mock.config = {'stacktrace': True}
                try:
                    templates.parse_tag(config, 'vault:', 'config={"invalid": "foobar"}:secret/mysecret')
                except E2j2Exception as error:
                    self.assertEqual(str(error), 'config validation failed')
                    stdout_mock.assert_called_with(Contains('Traceback'))

        # invalid json in config
        try:
            templates.parse_tag(config, 'vault:', 'config={"<invalid>"}::secret/mysecret')
        except E2j2Exception as error:
            self.assertEqual(str(error), 'decoding JSON failed')

        # unknown tag
        self.assertEqual(templates.parse_tag(config, 'unknown:', 'foobar'),
                         (None, '** ERROR: tag: unknown: not implemented **'))

    def test_stdout(self):
        with patch('e2j2.helpers.templates.sys.stdout.write') as stdout_mock:
            templates.stdout('logline')
            stdout_mock.assert_called_with('logline')

        with patch('e2j2.helpers.templates.sys.stdout.write') as stdout_mock:
            with patch('e2j2.helpers.templates.cache') as cache_mock:
                cache_mock.log_repeat_log_msg_counter = 1
                cache_mock.print_at = 2
                cache_mock.increment = 2
                templates.stdout('logline')  # show
                templates.stdout('logline')
                templates.stdout('logline')  # show
                templates.stdout('logline')
                templates.stdout('logline')
                templates.stdout('logline')
                templates.stdout('logline')  # show
                stdout_mock.assert_has_calls([call('logline'), call('(2x) logline'), call('(4x) logline')])


if __name__ == '__main__':
    unittest.main()
