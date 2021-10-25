from mock import patch
from e2j2 import cli


def test_get_files_with_filelist():
    # with file_list
    assert cli.get_files(filelist=['file1.j2', 'file2.j2'], searchlist=None, extension=None, recurse=None) == ['file1.j2', 'file2.j2']


@patch('e2j2.templates.find')
def test_get_files_without_filelist(find_mocker):
    find_mocker.return_value = ['file1.j2', 'file2.j2']
    assert cli.get_files(filelist=None, searchlist='/foo/bar', extension='.j2', recurse=None) == ['file1.j2', 'file2.j2']
