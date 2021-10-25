from mock import patch
from e2j2 import cli
from callee import Contains
from subprocess import CalledProcessError
import pytest


@pytest.fixture(autouse=True)
def get_files_mocker():
    with patch("e2j2.cli.get_files", return_value=["/foo/file1.j2"]):
        yield


@pytest.fixture(autouse=True)
def dirname_mocker():
    with patch("e2j2.cli.os.path.dirname", side_effect=["foo"]):
        yield


@pytest.fixture(autouse=True)
def render_template_mocker():
    with patch("e2j2.templates.render", side_effect=["file1 content"]):
        yield


@pytest.fixture(autouse=True)
def display_mocker():
    with patch("e2j2.cli.write"):
        yield


@patch("e2j2.cli.write_file")
def test_run(write_file_mocker, argument_parser):
    args = argument_parser
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 0
    write_file_mocker.assert_called_with("/foo/file1", "file1 content")


@patch("e2j2.cli.write")
def test_run_with_noop_set(display_mocker, argument_parser):
    args = argument_parser
    args.noop = True
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 0
    display_mocker.assert_called_with("skipped\n")


@patch("e2j2.cli.write_file")
def test_run_with_filelist_set(write_file_mocker, argument_parser):
    args = argument_parser
    args.filelist = "/foo/file1.j2"
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 0
    write_file_mocker.assert_called_with("/foo/file1", "file1 content")


@patch("e2j2.cli.write_file")
def test_run_with_multiple_files(write_file_mocker, argument_parser):
    args = argument_parser
    args.filelist = "/foo/file1.j2"
    config = cli.configure(args)
    with patch("e2j2.cli.get_files", return_value=["/foo/file2.j2", "/bar/file3.j2"]):
        with patch("e2j2.cli.os.path.dirname", side_effect=["foo", "bar"]):
            with patch(
                "e2j2.templates.render", side_effect=["file2 content", "file3 content"]
            ):
                exit_code = cli.run(config)
                assert exit_code == 0
                assert write_file_mocker.call_count == 2


@patch("e2j2.cli.write_file")
@patch("e2j2.cli.copy_file_permissions")
def test_run_with_copy_file_permissions_set(
    copy_file_permissions_mocker, _, argument_parser
):
    args = argument_parser
    args.copy_file_permissions = True
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 0
    copy_file_permissions_mocker.assert_called_with("/foo/file1.j2", "/foo/file1")


@patch("e2j2.cli.write_file")
@patch("e2j2.cli.subprocess.check_output")
def test_run_with_run_set(subprocess_mocker, _, argument_parser):
    args = argument_parser
    args.run = ["/foobar.sh"]
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 0
    subprocess_mocker.assert_called_with(["/foobar.sh"], stderr=-2)


@patch("e2j2.cli.write_file")
@patch("e2j2.cli.write")
def test_failed_ioerror_raised(display_mocker, write_file_mocker, argument_parser):
    write_file_mocker.side_effect = IOError()
    args = argument_parser
    args.stderr = True
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 1
    display_mocker.assert_called_with("failed ()\n")


@patch("e2j2.cli.write_file")
@patch("e2j2.templates.render")
def test_failed_with_traceback_set(render_mocker, write_file_mocker, argument_parser):
    render_mocker.side_effect = KeyError("Error")
    args = argument_parser
    args.stacktrace = True
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 1
    write_file_mocker.assert_called_with("/foo/file1.err", Contains("Error"))
    write_file_mocker.assert_called_with("/foo/file1.err", Contains("Traceback"))

@patch("e2j2.cli.write_file")
@patch("e2j2.templates.render")
def test_failed_with_strerr_set(render_mocker, _, argument_parser):
    render_mocker.side_effect = KeyError("Error")
    args = argument_parser
    args.stderr = True
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 1


@patch("e2j2.cli.write_file")
@patch("e2j2.cli.subprocess.check_output")
def test_failed_run_with_run_set(subprocess_mocker, _, argument_parser):
    subprocess_mocker.side_effect = CalledProcessError(
        cmd="./foobar.sh", returncode=1, output=b"error in foobar.sh"
    )
    args = argument_parser
    args.run = ["/foobar.sh"]
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 1


@patch("e2j2.templates.render")
def test_failed_run_with_run_set_render_error(render_mocker, argument_parser):
    render_mocker.side_effect = KeyError("Error")
    args = argument_parser
    args.run = ["/foobar.sh"]
    config = cli.configure(args)
    exit_code = cli.run(config)
    assert exit_code == 1
