import unittest
from mock import patch, mock_open
from callee import Contains
from subprocess import CalledProcessError
from e2j2 import cli
from e2j2.exceptions import E2j2Exception


class ArgumentParser:
    def __init__(self):
        self.filelist = []
        self.searchlist = None
        self.recursive = False
        self.ext = '.j2'
        self.no_color = True
        self.twopass = False
        self.nested_tags = False
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
        self.run = None
        self.noop = False
        self.splay = 0
        self.initial_run = False
        self.skip_render_on_undef = False
        self.marker_set = '{{'
        self.autodetect_marker_set = False


class TestCli(unittest.TestCase):
    def setUp(self):
        pass

    def test_arg_parse(self):
        argument_parser = ArgumentParser()
        with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
            args = cli.arg_parse('e2j2', '', 'x.x.x')
            self.assertEqual(args.searchlist, None)
            self.assertFalse(args.recursive)

        # test conflicting params
        argument_parser = ArgumentParser()
        argument_parser.searchlist = []
        argument_parser.recursive = True
        with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
            with patch('sys.stderr'):
                with self.assertRaisesRegex(SystemExit, '2'):
                    _ = cli.arg_parse('e2j2', '', 'x.x.x')
        argument_parser.recursive = False

        argument_parser = ArgumentParser()
        argument_parser.splay = True
        argument_parser.watchlist = []
        with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
            with patch('sys.stderr') as stderr_mock:
                with self.assertRaisesRegex(SystemExit, '2'):
                    _ = cli.arg_parse('e2j2', '', 'x.x.x')
                    stderr_mock.assert_called_with()
        argument_parser.splay = False

        argument_parser = ArgumentParser()
        argument_parser.initial_run = True
        argument_parser.watchlist = []
        argument_parser.run = []
        with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
            with patch('sys.stderr') as stderr_mock:
                with self.assertRaisesRegex(SystemExit, '2'):
                    _ = cli.arg_parse('e2j2', '', 'x.x.x')
                    stderr_mock.assert_called_with()

        argument_parser = ArgumentParser()
        argument_parser.initial_run = True
        argument_parser.watchlist = ['FOO']
        argument_parser.run = []
        with patch('e2j2.cli.argparse.ArgumentParser.parse_args', return_value=argument_parser):
            with patch('sys.stderr') as stderr_mock:
                with self.assertRaisesRegex(SystemExit, '2'):
                    _ = cli.arg_parse('e2j2', '', 'x.x.x')
                    stderr_mock.assert_called_with()

    def test_get_files(self):
        # with file_list
        self.assertEqual(
            cli.get_files(filelist=['file1.j2', 'file2.j2'], searchlist=None, extension=None, recurse=None),
            ['file1.j2', 'file2.j2'],
        )

        # without filelist
        with patch('e2j2.templates.find', return_value=['file1.j2', 'file2.j2']):
            self.assertEqual(
                cli.get_files(filelist=None, searchlist='/foo/bar', extension='.j2', recurse=None),
                ['file1.j2', 'file2.j2'],
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
        args = ArgumentParser()
        args.config = 'config.json'
        open_mock = mock_open(read_data='{"searchlist": ["/foo"]}')
        with patch('e2j2.cli.open', open_mock):
            self.assertEqual(cli.configure(args)['searchlist'], ['/foo'])

        open_mock = mock_open()
        # Handle IO error
        open_mock.side_effect = IOError('IOError')
        with patch('e2j2.display.write') as display_mock:
            with patch('e2j2.cli.open', open_mock):
                with self.assertRaisesRegex(IOError, 'IOError'):
                    _ = cli.configure(args)
                    display_mock.assert_called_with('E2J2 configuration error: IOError')

        args.initial_run = True
        args.watchlist = None
        args.run = None
        args.config = None
        with self.assertRaisesRegex(E2j2Exception, 'required: watchlist, run'):
            _ = cli.configure(args)

    def test_watch(self):
        config = {'watchlist': ['foo'], 'no_color': True, 'splay': 0, 'run': [], 'initial_run': False}
        # with change
        with patch('e2j2.cli.sleep', side_effect=KeyboardInterrupt):
            with patch('e2j2.cli.write') as display_mock:
                with patch('e2j2.cli.get_vars', return_value={"FOO": "BAR"}):
                    with patch('e2j2.cli.Thread') as thread_mock:
                        cli.watch(config)
                        thread_mock.assert_called_with(target=cli.watch_run, args=(config,))

                # key error raised
                with patch('e2j2.cli.get_vars', side_effect=KeyError('FOO')):
                    cli.watch(config)
                    display_mock.assert_called_with(Contains("unknown key 'FOO'"))

    def test_watch_run(self):
        config = {'no_color': True, 'noop': False}

        with patch('e2j2.cli.write'):
            # normal run

            with patch('e2j2.cli.run', side_effect=[0, 0]) as run_mock:
                exit_code = cli.watch_run(config)
                self.assertEqual(2, run_mock.call_count)
                self.assertEqual(0, exit_code)

            # failed
            with patch('e2j2.cli.run', return_value=1) as run_mock:
                exit_code = cli.watch_run(config)
                self.assertEqual(1, run_mock.call_count)
                self.assertEqual(1, exit_code)

            # noop
            config['noop'] = True
            with patch('e2j2.cli.run', return_value=0) as run_mock:
                exit_code = cli.watch_run(config)
                self.assertEqual(1, run_mock.call_count)
                self.assertEqual(0, exit_code)

    def test_run(self):
        args = ArgumentParser()
        # FIXME replace all args.filelist.split with lists see normal run
        # noop run
        args.noop = True
        config = cli.configure(args)
        with patch('e2j2.cli.get_files', return_value=['/foo/file1.j2']):
            with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                with patch('e2j2.templates.render', side_effect=['content1']):
                    with patch('e2j2.cli.write') as display_mock:
                        exit_code = cli.run(config)
                        self.assertEqual(0, exit_code)
                        display_mock.assert_called_with('skipped\n')

        args.noop = False

        # normal run
        config = cli.configure(args)
        with patch('e2j2.cli.write'):
            with patch('e2j2.cli.get_files', return_value=['/foo/file1.j2']):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.templates.render', side_effect=['file1 content']):
                        with patch('e2j2.cli.write_file') as write_mock:
                            exit_code = cli.run(config)
                            self.assertEqual(exit_code, 0)
                            write_mock.assert_called_with('/foo/file1', 'file1 content')

        # normal run with filelist flag set
        args.filelist = '/foo/file1.j2'
        config = cli.configure(args)
        with patch('e2j2.cli.write'):
            with patch('e2j2.templates.render', side_effect=['file1 content']):
                with patch('e2j2.cli.write_file') as write_mock:
                    exit_code = cli.run(config)
                    self.assertEqual(exit_code, 0)
                    write_mock.assert_called_with('/foo/file1', 'file1 content')
        args.filelist = []

        # normal run with two files
        config = cli.configure(args)
        with patch('e2j2.cli.write'):
            with patch('e2j2.cli.get_files', return_value=['/foo/file2.j2', '/bar/file3.j2']):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo', 'bar']):
                    with patch('e2j2.templates.render', side_effect=['file2 content', 'file3 content']):
                        with patch('e2j2.cli.write_file') as write_mock:
                            exit_code = cli.run(config)
                            self.assertEqual(exit_code, 0)
                            self.assertEqual(2, write_mock.call_count)

        # IOError raised
        config = cli.configure(args)
        with patch('e2j2.cli.get_files', return_value=['/foo/file4.j2']):
            with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                with patch('e2j2.templates.render', side_effect=['file4 content']):
                    with patch('e2j2.cli.write_file') as write_mock:
                        with patch('e2j2.cli.write') as display_mock:
                            write_mock.side_effect = IOError()
                            exit_code = cli.run(config)
                            self.assertEqual(exit_code, 1)
                            display_mock.assert_called_with('failed ()\n')

        # KeyError raised including stacktrace
        args.stacktrace = True
        config = cli.configure(args)
        with patch('e2j2.cli.write'):
            with patch('e2j2.cli.get_files', return_value=['/foo/file1.j2']):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.templates.render') as render_mock:
                        render_mock.side_effect = KeyError('Error')
                        with patch('e2j2.cli.write_file') as write_mock:
                            exit_code = cli.run(config)
                            self.assertEqual(exit_code, 1)
                            write_mock.assert_called_with('/foo/file1.err', Contains('Error'))
                            write_mock.assert_called_with('/foo/file1.err', Contains('Traceback'))

        # set permissions
        args.copy_file_permissions = True
        config = cli.configure(args)
        with patch('e2j2.cli.write'):
            with patch('e2j2.cli.get_files', return_value=['/foo/file1.j2']):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.templates.render', side_effect=['file1 content']):
                        with patch('e2j2.cli.write_file'):
                            with patch('e2j2.cli.copy_file_permissions') as permission_mock:
                                cli.run(config)
                                permission_mock.assert_called_with('/foo/file1.j2', '/foo/file1')
        args.copy_file_permissions = False

        # run command
        args.run = ['/foobar.sh']
        config = cli.configure(args)
        with patch('e2j2.cli.write'):
            with patch('e2j2.cli.get_files', return_value=['/foo/file1.j2']):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.templates.render', side_effect=['file1 content']):
                        with patch('e2j2.cli.write_file'):
                            with patch('e2j2.cli.subprocess.check_output') as subprocess_mock:
                                exit_code = cli.run(config)
                                self.assertEqual(exit_code, 0)
                                subprocess_mock.assert_called_with(['/foobar.sh'], stderr=-2)

            # run command with error
            with patch('e2j2.cli.get_files', return_value=['/foo/file1.j2']):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.templates.render', side_effect=['file1 content']):
                        with patch('e2j2.cli.write_file'):
                            with patch('e2j2.cli.subprocess.check_output') as subprocess_mock:
                                subprocess_mock.side_effect = CalledProcessError(
                                    cmd='./foobar.sh', returncode=1, output=b'error in foobar.sh'
                                )
                                exit_code = cli.run(config)
                                self.assertEqual(exit_code, 1)

        # run skipped due to rendering error
        with patch('e2j2.cli.write') as display_mock:
            with patch('e2j2.cli.get_files', return_value=['/foo/file1.j2']):
                with patch('e2j2.cli.os.path.dirname', side_effect=['foo']):
                    with patch('e2j2.templates.render', side_effect=['file1 content']):
                        with patch('e2j2.cli.write_file') as write_mock:
                            write_mock.side_effect = IOError()
                            with patch('e2j2.cli.subprocess.check_output') as subprocess_mock:
                                exit_code = cli.run(config)
                                self.assertEqual(exit_code, 1)
                                self.assertEqual(subprocess_mock.call_count, 0)
                                display_mock.assert_called_with(Contains('skipped'))
        args.run = None

    def test_e2j2(self):
        args = ArgumentParser()
        args.stacktrace = True

        # Handle exceptions in config with stacktrace
        config = {'no_color': False}
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.configure', side_effect=IOError('config.json not found')):
                with patch('e2j2.cli.write') as display_mock:
                    error_code = cli.e2j2()
                    display_mock.assert_any_call('E2J2 configuration error: config.json not found')
                    display_mock.assert_any_call(Contains('Traceback'))
                    self.assertEqual(1, error_code)

        # test exit_codes from calling run()
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.run', return_value=0):
                error_code = cli.e2j2()
                self.assertEqual(0, error_code)

        # watch
        args.watchlist = 'FOOBAR'
        with patch('e2j2.cli.arg_parse', return_value=args):
            with patch('e2j2.cli.watch') as watch_mock:
                cli.e2j2()
                watch_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
