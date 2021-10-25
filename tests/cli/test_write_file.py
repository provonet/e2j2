from mock import patch, mock_open
from e2j2 import cli


def test_write_file():
    with patch('e2j2.cli.open', mock_open()) as open_mock:
        cli.write_file('file.txt', 'content')
        open_mock.assert_called_with('file.txt', mode='w')
