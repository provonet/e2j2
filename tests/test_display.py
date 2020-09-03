import unittest
from mock import patch, call
from e2j2 import display


class TestDsiplay(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_stdout(self):
        with patch('e2j2.display.sys.stdout.write') as stdout_mock:
            display.stdout('logline')
            stdout_mock.assert_called_with('logline')

        with patch('e2j2.display.sys.stdout.write') as stdout_mock:
            with patch('e2j2.display.cache') as cache_mock:
                cache_mock.log_repeat_log_msg_counter = 1
                cache_mock.print_at = 2
                cache_mock.increment = 2
                display.stdout('logline')  # show
                display.stdout('logline')
                display.stdout('logline')  # show
                display.stdout('logline')
                display.stdout('logline')
                display.stdout('logline')
                display.stdout('logline')  # show
                stdout_mock.assert_has_calls([call('logline'), call('(2x) logline'), call('(4x) logline')])

    def test_display(self):
        config = {'no_color': True,
                  'colors': {
                    'bright_red': '',
                    'green': '',
                    'lightgreen': '',
                    'white': '',
                    'yellow': '',
                    'reset_all': ''
                    }
                  }

        with patch('e2j2.display.stdout') as stdout_mock:
            display.display(config, 'foobar')
            stdout_mock.assert_has_calls([call('foobar')])
