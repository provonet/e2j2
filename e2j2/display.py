import sys
from string import Template
from e2j2 import cache
from e2j2.constants import BRIGHT_RED, GREEN, LIGHTGREEN, YELLOW, WHITE, RESET_ALL



def stdout(msg):
    print_at = cache.print_at
    increment = cache.increment
    counter = cache.log_repeat_log_msg_counter

    if cache.last_log_line != msg:
        sys.stdout.write(msg)
        cache.log_repeat_log_msg_counter = 0
    elif counter == print_at:
        sys.stdout.write('({}x) '.format(print_at) + msg)
        cache.print_at += increment
        cache.log_repeat_log_msg_counter = 0

    cache.log_repeat_log_msg_counter += 1
    cache.last_log_line = msg


def display(config, text):
    colors = config['colors']
    template = Template(text)
    stdout(template.substitute(bright_red=colors['bright_red'], green=colors['green'], lightgreen=colors['lightgreen'], white=colors['white'], yellow=colors['yellow'],
                               reset_all=colors['reset_all']))
