import unittest
from mock import patch, MagicMock
from callee import Contains
from e2j2 import templates
from e2j2.exceptions import E2j2Exception
from jinja2.exceptions import UndefinedError, FilterArgumentError, TemplateSyntaxError

markers = {
    'block_start': '{%',
    'block_end': '%}',
    'variable_start': '{{',
    'variable_end': '}}',
    'comment_start': '{#',
    'comment_end': '#}',
    'config_start': '{',
    'config_end': '}',
}


class TestTemplates(unittest.TestCase):
    def setUp(self):
        pass

    def test_find(self):
        # recurse = True
        with patch('e2j2.templates.os.walk') as recurse_mock:
            templates.find(searchlist=['/etc'], j2file_ext='.j2', recurse=True)
            recurse_mock.assert_called_with('/etc', followlinks=True)

        # recurse = False
        with patch('e2j2.templates.os.listdir') as dirlist_mock:
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
        self.assertEqual(list(templates.recursive_iter(data)), [(('listofdict', 0), {'test_key', 'test_value'})])

    def test_get_vars(self):
        config = {'no_color': True, 'twopass': True, 'nested_tags': False}
        with patch('e2j2.templates.detect_markers', return_value=markers):
            with patch('e2j2.templates.os') as os_mock:
                os_mock.environ = {'FOO_ENV': 'json:{"key": "value"}'}
                self.assertEqual(
                    templates.get_vars(config, whitelist=['FOO_ENV'], blacklist=[]), {'FOO_ENV': {'key': 'value'}}
                )

                # whitelist / blacklist
                self.assertEqual(templates.get_vars(config, whitelist=['FOO_ENV'], blacklist=['FOO_ENV']), {})

    def test_resolv_vars(self):
        config = {'no_color': True, 'nested_tags': False}

        with patch('e2j2.templates.detect_markers', return_value=markers):
            with patch('e2j2.templates.parse_tag', side_effect=E2j2Exception('foobar error')):
                with patch('e2j2.templates.write') as display_mock:
                    templates.resolv_vars(config, var_list=['FOO_ENV'], env_vars={'FOO_ENV': 'json:{"key": "value"}'})
                    display_mock.assert_called_with(Contains('foobar error'))

            # test normal rendering
            self.assertEqual(
                templates.resolv_vars(
                    config, var_list=['FOO_ENV'], env_vars={'FOO_ENV': 'json:{"key": "base64:dmFsdWU="}'}
                ),
                {'FOO_ENV': {'key': 'base64:dmFsdWU='}},
            )

            # test Nested vars
            config['nested_tags'] = True

            # test string with nested base64 tag
            self.assertEqual(
                templates.resolv_vars(
                    config, var_list=['FOO_ENV'], env_vars={'FOO_ENV': 'json:{"key": "base64:dmFsdWU="}'}
                ),
                {'FOO_ENV': {'key': 'value'}},
            )

            # test string with nested file tag raising an error
            with patch(
                'e2j2.templates.file_tag.parse',
                side_effect=E2j2Exception('IOError raised while reading file: /foobar.txt'),
            ):
                with patch('e2j2.templates.write') as display_mock:
                    templates.resolv_vars(
                        config, var_list=['FOO_ENV'], env_vars={'FOO_ENV': 'json:{"key": "file:/foobar.txt"}'}
                    )
                    display_mock.assert_called_with(Contains('failed to resolve nested tag'))

            # test with string value
            self.assertEqual(
                templates.resolv_vars(config, var_list=['FOO_ENV'], env_vars={'FOO_ENV': 'json:{"key": "value"}'}),
                {'FOO_ENV': {'key': 'value'}},
            )

            # test with boolean value
            self.assertEqual(
                templates.resolv_vars(config, var_list=['FOO_ENV'], env_vars={'FOO_ENV': 'json:{"key": true}'}),
                {'FOO_ENV': {'key': True}},
            )

            # test with integer value
            self.assertEqual(
                templates.resolv_vars(config, var_list=['FOO_ENV'], env_vars={'FOO_ENV': 'json:{"key": 1}'}),
                {'FOO_ENV': {'key': 1}},
            )

            # test with config flatten=True return value from call should return a dict with a foobar key
            self.assertTrue(
                'foobar'
                in templates.resolv_vars(
                    config,
                    var_list=['FOO_ENV'],
                    env_vars={'FOO_ENV': 'json:config={"flatten": true}:{"foobar": "foobar_value"}'},
                )
            )

            # test with config flatten=False return value from call should not have a foobar key
            self.assertTrue(
                'foobar'
                not in templates.resolv_vars(
                    config,
                    var_list=['FOO_ENV'],
                    env_vars={'FOO_ENV': 'json:config={"flatten": false}:{"foobar": "foobar_value"}'},
                )
            )

    def test_render(self):
        config = {'no_color': True, 'twopass': False}
        with patch('e2j2.templates.detect_markers', return_value=markers):
            with patch('e2j2.templates.jinja2.Environment') as jinja2_mock:
                with patch('builtins.open') as file_mock:
                    # one pass
                    jinja2_mock.return_value.from_string.return_value.render.return_value = 'rendered template'
                    response = templates.render(config=config, j2file='/foo/file1.j2', j2vars={"FOO": "BAR"})

                    file_mock.assert_called_with('/foo/file1.j2', 'r')
                    jinja2_mock.return_value.from_string.return_value.render.assert_called_with({"FOO": "BAR"})
                    self.assertEqual(response, 'rendered template')

                    # two pass
                    config['twopass'] = True
                    jinja2_mock.return_value.from_string.return_value.render.return_value = 'rendered template'
                    response = templates.render(config=config, j2file='/foo/file1.j2', j2vars={"FOO": "BAR"})

                    jinja2_mock.return_value.from_string.assert_called_with('rendered template')
                    jinja2_mock.return_value.from_string.return_value.render.assert_called_with({"FOO": "BAR"})
                    self.assertEqual(response, 'rendered template')
                    config['twopass'] = False

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
                j2.from_string = MagicMock(return_value=template)
                with patch('builtins.open'):
                    with patch('e2j2.templates.jinja2.Environment', return_value=j2):
                        with self.assertRaisesRegex(E2j2Exception, 'at line'):
                            _ = templates.render(config=config, j2file='/foo/file1.j2', j2vars={"FOO": "BAR"})

            # template not found exception
            template.render = MagicMock(side_effect=FileNotFoundError())
            j2.get_template = MagicMock(return_value=template)
            with patch('builtins.open'):
                with patch('e2j2.templates.jinja2.Environment', return_value=j2):
                    with self.assertRaisesRegex(E2j2Exception, 'Template file1.j2 not found'):
                        _ = templates.render(config=config, j2file='/foo/file1.j2', j2vars={"FOO": "BAR"})

                # other exceptions
                template.render = MagicMock(side_effect=ValueError('Error'))
                j2.get_template = MagicMock(return_value=template)
                with patch('e2j2.templates.jinja2.Environment', return_value=j2):
                    with self.assertRaisesRegex(E2j2Exception, 'Error'):
                        _ = templates.render(config=config, j2file='/foo/file1.j2', j2vars={"FOO": "BAR"})

    def test_parse_tag(self):
        config = {
            'stacktrace': True,
            'no_color': True,
            'twopass': True,
            'marker_set': '{{',
            'autodetect_marker_set': False,
            'nested_tags': False,
        }
        config.update(markers)

        with patch('e2j2.templates.json_tag.parse') as json_mock:
            templates.parse_tag(config, 'json:', '{}')
            json_mock.assert_called_with('{}')

        with patch('e2j2.templates.jsonfile_tag.parse') as jsonfile_mock:
            templates.parse_tag(config, 'jsonfile:', 'file.json')
            jsonfile_mock.assert_called_with('file.json')

        with patch('e2j2.templates.base64_tag.parse') as base64_mock:
            templates.parse_tag(config, 'base64:', 'Zm9vYmFy')
            base64_mock.assert_called_with('Zm9vYmFy')

        with patch('e2j2.templates.consul_tag.parse') as consul_mock:
            templates.parse_tag(config, 'consul:', 'consulkey')
            consul_mock.assert_called_with({}, 'consulkey')

        with patch('e2j2.templates.list_tag.parse') as list_mock:
            templates.parse_tag(config, 'list:', 'foo,bar')
            list_mock.assert_called_with('foo,bar')

        with patch('e2j2.templates.file_tag.parse') as file_mock:
            templates.parse_tag(config, 'file:', 'file.txt')
            file_mock.assert_called_with('file.txt')

        # no config
        with patch('e2j2.templates.vault_tag.parse') as vault_mock:
            templates.parse_tag(config, 'vault:', 'secret/mysecret')
            vault_mock.assert_called_with({}, 'secret/mysecret')

        with patch('e2j2.templates.escape_tag.parse') as escape_mock:
            templates.parse_tag(config, 'escape:', 'file:foobar')
            escape_mock.assert_called_with('file:foobar')

        # with config
        with patch('e2j2.templates.json_tag.parse') as json_mock:
            templates.parse_tag(
                config, 'json:', 'json:config={"flatten": true}:{"key": {"nested": "flattened json example"}}'
            )
            json_mock.assert_called_with('{"key": {"nested": "flattened json example"}}')

        # with config and alternative marker [, ]
        config['config_start'] = '['
        config['config_end'] = ']'
        with patch('e2j2.templates.vault_tag.parse') as vault_mock:
            templates.parse_tag(config, 'vault:', 'config=["url": "https://localhost:8200"]:secret/mysecret')
            vault_mock.assert_called_with({"url": "https://localhost:8200"}, 'secret/mysecret')

        # with config and alternative marker [, ] but without twopass
        config['twopass'] = False
        config['marker_set'] = '{{'
        config['config_start'] = None
        config['config_end'] = None
        with patch('e2j2.templates.vault_tag.parse'):
            with self.assertRaisesRegex(E2j2Exception, 'invalid config markers used'):
                templates.parse_tag(config, 'vault:', 'config=["url": "https://localhost:8200"]:secret/mysecret')

        config['twopass'] = True
        # with config and alternative marker <, >
        config['config_start'] = '<'
        config['config_end'] = '>'
        with patch('e2j2.templates.vault_tag.parse') as vault_mock:
            templates.parse_tag(
                config, 'vault:', 'config=<"url": "https://localhost:8200", "token": "aabbccddee">:secret/mysecret'
            )
            vault_mock.assert_called_with({"url": "https://localhost:8200", "token": "aabbccddee"}, 'secret/mysecret')

        # with config and alternative marker (, )
        config['config_start'] = '('
        config['config_end'] = ')'
        with patch('e2j2.templates.vault_tag.parse') as vault_mock:
            templates.parse_tag(config, 'vault:', 'config=("url": "https://localhost:8200"):secret/mysecret')
            vault_mock.assert_called_with({"url": "https://localhost:8200"}, 'secret/mysecret')

        config['config_start'] = '{'
        config['config_end'] = '}'

        # with envar config
        with patch('e2j2.templates.os') as os_mock:
            os_mock.environ = {'VAULT_CONFIG': '{"url": "https://localhost:8200"}'}
            with patch('e2j2.templates.vault_tag.parse') as vault_mock:
                templates.parse_tag(config, 'vault:', 'secret/mysecret')
                vault_mock.assert_called_with({"url": "https://localhost:8200"}, 'secret/mysecret')

        # with envvar config and token envvar
        with patch('e2j2.templates.os') as os_mock:
            os_mock.environ = {'VAULT_CONFIG': '{"url": "https://localhost:8200"}', 'VAULT_TOKEN': 'aabbccddee'}
            with patch('e2j2.templates.vault_tag.parse') as vault_mock:
                templates.parse_tag(config, 'vault:', 'secret/mysecret')
                vault_mock.assert_called_with(
                    {'url': 'https://localhost:8200', 'token': 'aabbccddee'}, 'secret/mysecret'
                )

        config['twopass'] = False
        config['marker_set'] = '{{'
        config['config_start'] = None
        config['config_end'] = None
        with patch('e2j2.templates.file_tag.parse', return_value='aabbccddee') as file_mock:
            with patch('e2j2.templates.vault_tag.parse') as vault_mock:
                templates.parse_tag(
                    config,
                    'vault:',
                    'config={"url": "https://localhost:8200", "token": "file:/tmp/myfile"}:secret/mysecret',
                )
                vault_mock.assert_called_with(
                    {'url': 'https://localhost:8200', 'token': 'aabbccddee'}, 'secret/mysecret'
                )

        with patch('e2j2.templates.dns_tag.parse') as dns_mock:
            templates.parse_tag(config, 'dns:', 'config={"type": "MX"}:mx.foo.bar')
            dns_mock.assert_called_with({'type': 'MX'}, 'mx.foo.bar')

        # with config
        with patch('e2j2.templates.dns_tag.parse') as dns_mock:
            templates.parse_tag(config, 'dns:', 'www.foo.bar')
            dns_mock.assert_called_with({}, 'www.foo.bar')

        # schema validation error including stacktrace
        with patch('e2j2.display._cache') as cache_mock:
            with patch('e2j2.templates.write') as display_mock:
                cache_mock.config = {'stacktrace': True}
                try:
                    templates.parse_tag(config, 'vault:', 'config={"invalid": "foobar"}:secret/mysecret')
                except E2j2Exception as error:
                    self.assertEqual(str(error), 'config validation failed')
                    display_mock.assert_called_with(Contains('Traceback'))

        # invalid json in config
        try:
            templates.parse_tag(config, 'vault:', 'config={"<invalid>"}::secret/mysecret')
        except E2j2Exception as error:
            self.assertEqual(str(error), 'decoding JSON failed')

        # unknown tag
        self.assertEqual(
            templates.parse_tag(config, 'unknown:', 'foobar'), (None, '** ERROR: tag: unknown: not implemented **')
        )

    def test_detect_markers(self):
        config = {
            'marker_set': '{{',
            'block_start': None,
            'block_end': None,
            'variable_start': None,
            'variable_end': None,
            'comment_start': None,
            'comment_end': None,
            'config_start': None,
            'config_end': None,
            'autodetect_marker_set': True,
        }

        config_overwrite = config.copy()
        config_overwrite.update(markers)

        expected_response = {
            'block_start': '{%',
            'block_end': '%}',
            'variable_start': '{{',
            'variable_end': '}}',
            'comment_start': '{#',
            'comment_end': '#}',
            'config_start': '{',
            'config_end': '}',
        }

        # autodetect off
        config['autodetect_marker_set'] = False
        self.assertEqual(templates.detect_markers(config, ''), expected_response)

        # autodetect on / test fallback
        config['autodetect_marker_set'] = True
        self.assertEqual(templates.detect_markers(config, ''), expected_response)

        # autodetect on / overwrite
        self.assertEqual(templates.detect_markers(config_overwrite, '(==)'), expected_response)

        expected_response = {
            'block_start': '[%',
            'block_end': '%]',
            'variable_start': '[=',
            'variable_end': '=]',
            'comment_start': '[#',
            'comment_end': '#]',
            'config_start': '[',
            'config_end': ']',
        }

        # autodetect on / config marker
        response = templates.detect_markers(config, 'vault:config=["url:", "http://foo.bar"]:secret')
        self.assertEqual(expected_response, response)

        expected_response = {
            'block_start': '(%',
            'block_end': '%)',
            'variable_start': '(=',
            'variable_end': '=)',
            'comment_start': '(#',
            'comment_end': '#)',
            'config_start': '(',
            'config_end': ')',
        }

        # autodetect on
        response = templates.detect_markers(config, '(==)')
        self.assertEqual(expected_response, response)


if __name__ == '__main__':
    unittest.main()
