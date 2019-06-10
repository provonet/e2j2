import unittest
import os
from mock import patch, mock_open
from e2j2 import cli
from e2j2.helpers.constants import BRIGHT_RED, RESET_ALL, GREEN, LIGHTGREEN, WHITE, YELLOW


class ArgumentParser:
    pass


class TestCli(unittest.TestCase):
    def setUp(self):
        pass

    def test_arg_parse(self):
        # no arguments
        with patch('sys.argv'):
            args = cli.arg_parse('e2j2', '', 'x.x.x')

            self.assertFalse(args.no_color)
            self.assertFalse(args.recursive)
            self.assertFalse(args.noop)
            self.assertFalse(args.twopass)

    def test_search_list(self):
        # default
        self.assertEqual(cli.get_search_list(None), '.')

        # set
        self.assertEqual(cli.get_search_list('foo,bar'), 'foo,bar')

        # from environment
        with patch('e2j2.cli.os.environ.get', return_value='foo,bar'):
            self.assertEqual(cli.get_search_list(None), 'foo,bar')

    def test_use_color(self):
        # use_color == True
        #  bright_red, green, lightgreen, white, yellow, reset_all = palette(not args.no_color)
        self.assertEqual(cli.use_color(True), (BRIGHT_RED, GREEN, LIGHTGREEN, WHITE, YELLOW, RESET_ALL))
        self.assertEqual(cli.use_color(False), ("",) * 6)

    def test_get_files(self):
        # with file_list
        self.assertEqual(
            cli.get_files(filelist='file1.j2,file2.j2', searchlist=None, extension=None, recurse=None),
            ['file1.j2', 'file2.j2']
        )

        # without filelist
        with patch('e2j2.helpers.templates.find', return_value=['file1.j2', 'file2.j2']):
            self.assertEqual(
                cli.get_files(filelist=None, searchlist='/foo/bar', extension='.j2', recurse=None),
                ['file1.j2', 'file2.j2']
            )

    def test_write_file(self):
        with patch('e2j2.cli.open', mock_open()) as open_mock:
            cli.write_file('file.txt', 'content')
            open_mock.assert_called_with('file.txt', mode='w')

    def test_e2j2(self):
        args = ArgumentParser()
        args.filelist = ['/foo/file1.j2']
        args.searchlist = None
        args.recursive = True
        args.ext = '.j2'
        args.no_color = True
        args.twopass = False
        args.block_start = '{%'
        args.block_end = '%}'
        args.variable_start = '{{'
        args.variable_end = '}}'
        args.comment_start = '{#'
        args.comment_end = '#}'
        args.env_whitelist = None
        args.env_blacklist = None

        # noop run
        args.noop = True
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.get_files', return_value=args.filelist):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.helpers.templates.render', side_effect=['content1']):
                        with patch('e2j2.cli.stdout') as stdout_mock:
                            exit_code = cli.e2j2()
                            self.assertEqual(exit_code, 0)
                            stdout_mock.assert_called_with('skipped\n')

        # normal run
        args.noop = False
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.get_files', return_value=args.filelist):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.helpers.templates.render', side_effect=['content1']):
                        with patch('e2j2.cli.write_file') as write_mock:
                            exit_code = cli.e2j2()
                            self.assertEqual(exit_code, 0)
                            write_mock.assert_called_with('/foo/file1', 'content1')

        # IOError raised
        args.noop = False
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.get_files', return_value=args.filelist):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.helpers.templates.render', side_effect=['content1']):
                        with patch('e2j2.cli.write_file') as write_mock:
                            with patch('e2j2.cli.stdout') as stdout_mock:
                                write_mock.side_effect = IOError()
                                exit_code = cli.e2j2()
                                self.assertEqual(exit_code, 1)
                                stdout_mock.assert_called_with('failed ()\n')

        # KeyError raised
        args.noop = False
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.get_files', return_value=args.filelist):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.helpers.templates.render') as render_mock:
                        render_mock.side_effect = KeyError('Error')
                        with patch('e2j2.cli.write_file') as write_mock:
                            exit_code = cli.e2j2()
                            self.assertEqual(exit_code, 1)
                            write_mock.assert_called_with('/foo/file1.err', "'Error'")


if __name__ == '__main__':
    unittest.main()
