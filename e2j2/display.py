import sys
from string import Template
from e2j2 import cache

BRIGHT_RED = "\033[1;31m"
RESET_ALL = "\033[00m"
YELLOW = "\033[93m"
GREEN = "\033[0;32m"
LIGHTGREEN = "\033[1;32m"
WHITE = "\033[0;37m"


class Colorize:
    red = BRIGHT_RED
    reset = RESET_ALL
    yellow = YELLOW
    green = GREEN
    lightgreen = LIGHTGREEN
    white = WHITE


_colors = Colorize()


def get_colors():
    return _colors


def colorize():
    global _colors
    _colors = Colorize()


def no_colors():
    global _colors
    _colors = Colorize()
    _colors.red = ''
    _colors.reset = ''
    _colors.yellow = ''
    _colors.green = ''
    _colors.lightgreen = ''
    _colors.white = ''


def write(msg):
    print_at = cache.print_at
    increment = cache.increment
    counter = cache.log_repeat_log_msg_counter

    if cache.last_log_line != msg:
        sys.stderr.write(msg)
        cache.log_repeat_log_msg_counter = 0
    elif counter == print_at:
        sys.stderr.write('({}x) '.format(print_at) + msg)
        cache.print_at += increment
        cache.log_repeat_log_msg_counter = 0

    cache.log_repeat_log_msg_counter += 1
    cache.last_log_line = msg


def display(text):
    template = Template(text)
    write(
        template.substitute(
            bright_red=_colors.red,
            green=_colors.green,
            lightgreen=_colors.lightgreen,
            white=_colors.white,
            yellow=_colors.yellow,
            reset_all=_colors.reset,
        )
    )
