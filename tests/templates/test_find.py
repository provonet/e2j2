from mock import patch
from e2j2.templates import find


@patch('e2j2.templates.os.listdir')
def test_find(dirlist_mock):
    # recurse = False
    find(searchlist=['/etc'], j2file_ext='.j2', recurse=False)
    dirlist_mock.assert_called_with('/etc')


@patch('e2j2.templates.os.walk')
def test_find_recurse(recurse_mock):
    # recurse = True
    find(searchlist=['/etc'], j2file_ext='.j2', recurse=True)
    recurse_mock.assert_called_with('/etc', followlinks=True)
