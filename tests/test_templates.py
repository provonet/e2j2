import unittest
import six
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

    @unittest.skipIf(six.PY2, "not compatible with Python 2")
    def test_get_vars(self):
        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'FOO_ENV': 'json:{"key": "value"}'}
            self.assertEqual(templates.get_vars(), {'FOO_ENV': {'key': 'value'}})

        with patch('e2j2.helpers.templates.os') as os_mock:
            os_mock.environ = {'FOO_ENV': 'json:{"key": "value"}'}

            with patch('builtins.print'):
                with patch('e2j2.helpers.templates.parsers.parse_tag', return_value='** ERROR: Key not found **'):
                    self.assertEqual(templates.get_vars(), {'FOO_ENV': '** ERROR: Key not found **'})

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


if __name__ == '__main__':
    unittest.main()
