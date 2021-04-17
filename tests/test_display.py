import unittest
from mock import patch, call
from e2j2 import display


class TestDsiplay(unittest.TestCase):
    def setUp(self):
        pass

    def test_stdout(self):
        with patch('e2j2.display.sys.stdout.write') as stdout_mock:
            display.write('logline')
            stdout_mock.assert_called_with('logline')

        with patch('e2j2.display.sys.stdout.write') as stdout_mock:
            with patch('e2j2.display._cache') as cache_mock:
                cache_mock.log_repeat_log_msg_counter = 1
                cache_mock.print_at = 2
                cache_mock.increment = 2
                display.write('logline')  # show
                display.write('logline')
                display.write('logline')  # show
                display.write('logline')
                display.write('logline')
                display.write('logline')
                display.write('logline')  # show
                stdout_mock.assert_has_calls([call('logline'), call('(2x) logline'), call('(4x) logline')])
