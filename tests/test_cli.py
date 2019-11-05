import unittest
from six import assertRaisesRegex
from mock import patch, mock_open, MagicMock
from callee import Contains
from e2j2 import cli
from e2j2.helpers.constants import BRIGHT_RED, RESET_ALL, GREEN, LIGHTGREEN, WHITE, YELLOW


class ArgumentParser:
    def __init__(self):
        self.filelist = '/foo/file1.j2'
        self.searchlist = None
        self.recursive = True
        self.ext = '.j2'
        self.no_color = True
        self.twopass = False
        self.block_start = '{%'
        self.block_end = '%}'
        self.variable_start = '{{'
        self.variable_end = '}}'
        self.comment_start = '{#'
        self.comment_end = '#}'
        self.env_whitelist = None
        self.env_blacklist = None
        self.copy_file_permissions = False
        self.stacktrace = False
        self.config = None
        self.watchlist = None
        self.noop = False


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

    def test_use_color(self):
        # use_color == True
        #  bright_red, green, lightgreen, white, yellow, reset_all = palette(not args.no_color)
        self.assertEqual(cli.use_color(True), (BRIGHT_RED, GREEN, LIGHTGREEN, WHITE, YELLOW, RESET_ALL))
        self.assertEqual(cli.use_color(False), ("",) * 6)

    def test_get_files(self):
        # with file_list
        self.assertEqual(
            cli.get_files(filelist=['file1.j2', 'file2.j2'], searchlist=None, extension=None, recurse=None),
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

    def test_copy_file_permissions(self):
        # assume that a file is owned by uid: 1000 and guid: 1000
        # and permissions are set to 644
        class Stat:
            def __init__(self):
                self.st_uid = 1000
                self.st_gid = 1000
                self.st_mode = [0o644]

            def __getitem__(self, item):
                return self.st_mode[item]

        # check is os.chown and os.chmod are called with the correct values
        stat = Stat()
        with patch('e2j2.cli.os.stat', return_value=stat):
            with patch('e2j2.cli.os.chown') as chown_mock:
                with patch('e2j2.cli.os.chmod') as chmod_mock:
                    cli.copy_file_permissions('bar.j2', 'bar')
                    chown_mock.assert_called_with('bar', 1000, 1000)
                    chmod_mock.assert_called_with('bar', 0o644)

    def test_configure(self):
        # Handle IO error
        args = ArgumentParser()
        args.config = 'config.json'
        open_mock = mock_open()
        open_mock.side_effect = IOError('IOError')
        with patch('e2j2.cli.stdout') as stdout_mock:
            with patch('e2j2.cli.open', open_mock):
                with assertRaisesRegex(self, IOError, 'IOError'):
                    _ = cli.configure(args)
                    stdout_mock.assert_called_with('E2J2 configuration error: IOError')

    def test_run(self):
        args = ArgumentParser()

        # noop run
        args.noop = True
        config = cli.configure(args)
        with patch('e2j2.cli.get_files', return_value=args.filelist.split(',')):
            with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                with patch('e2j2.helpers.templates.render', side_effect=['content1']):
                    with patch('e2j2.cli.stdout') as stdout_mock:
                        exit_code = cli.run(config)
                        self.assertEqual(exit_code, 0)
                        stdout_mock.assert_called_with('skipped\n')

        args.noop = False

        # normal run
        config = cli.configure(args)
        with patch('e2j2.cli.get_files', return_value=args.filelist.split(',')):
            with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                with patch('e2j2.helpers.templates.render', side_effect=['file1 content']):
                    with patch('e2j2.cli.write_file') as write_mock:
                        exit_code = cli.run(config)
                        self.assertEqual(exit_code, 0)
                        write_mock.assert_called_with('/foo/file1', 'file1 content')

        # normal run with two files
        config = cli.configure(args)
        with patch('e2j2.cli.get_files', return_value=['/foo/file2.j2', '/bar/file3.j2']):
            with patch('e2j2.cli.os.path.dirname', side_effect=['foo', 'bar']):
                with patch('e2j2.helpers.templates.render', side_effect=['file2 content', 'file3 content']):
                    with patch('e2j2.cli.write_file') as write_mock:
                        exit_code = cli.run(config)
                        self.assertEqual(exit_code, 0)
                        self.assertEqual(2, write_mock.call_count)

        # IOError raised
        config = cli.configure(args)
        with patch('e2j2.cli.get_files', return_value=['/foo/file4.j2']):
            with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                with patch('e2j2.helpers.templates.render', side_effect=['file4 content']):
                    with patch('e2j2.cli.write_file') as write_mock:
                        with patch('e2j2.cli.stdout') as stdout_mock:
                            write_mock.side_effect = IOError()
                            exit_code = cli.run(config)
                            self.assertEqual(exit_code, 1)
                            stdout_mock.assert_called_with('failed ()\n')

        # KeyError raised
        config = cli.configure(args)
        with patch('e2j2.cli.get_files', return_value=args.filelist.split(',')):
            with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                with patch('e2j2.helpers.templates.render') as render_mock:
                    render_mock.side_effect = KeyError('Error')
                    with patch('e2j2.cli.write_file') as write_mock:
                        exit_code = cli.run(config)
                        self.assertEqual(exit_code, 1)
                        write_mock.assert_called_with('/foo/file1.err', Contains('Error'))

        # set permissions
        args.copy_file_permissions = True
        config = cli.configure(args)
        with patch('e2j2.cli.get_files', return_value=args.filelist.split(',')):
            with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                with patch('e2j2.helpers.templates.render', side_effect=['file1 content']):
                    with patch('e2j2.cli.write_file'):
                        with patch('e2j2.cli.copy_file_permissions') as permission_mock:
                            cli.run(config)
                            permission_mock.assert_called_with('/foo/file1.j2', '/foo/file1')

    def test_e2j2(self):
        args = ArgumentParser()

        # Handle exceptions in config
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.configure', side_effect=FileNotFoundError('config.json not found')):
                with patch('e2j2.cli.stdout') as stdout_mock:
                    error_code = cli.e2j2()
                    stdout_mock.assert_called_with('E2J2 configuration error: config.json not found')
                    self.assertEqual(1, error_code)

        # test exit_codes from calling run()
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.run', return_value=0):
                error_code = cli.e2j2()
                self.assertEqual(0, error_code)

        # watch
        args.watchlist = 'FOOBAR'
        config = cli.configure(args)
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.Thread', return_value=MagicMock()) as thread_mock:
                cli.e2j2()
                thread_mock.assert_called_with(target=cli.watch, args=(config, ), daemon=True)


if __name__ == '__main__':
    unittest.main()
