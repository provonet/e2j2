from mock import patch, mock_open
from e2j2 import cli


@patch('os.stat')
@patch('os.chown')
@patch('os.chmod')
def test_copy_file_permissions(chmod_mocker, chown_mocker, stat_mocker):
    stat_mocker.return_value.st_uid = 'luser'
    stat_mocker.return_value.st_gid = 'lusers'
    cli.copy_file_permissions('source_file', 'destination_file')

    chown_mocker.assert_called_with('destination_file', 'luser', 'lusers')
    assert chmod_mocker.called
