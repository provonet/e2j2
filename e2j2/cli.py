import sys
import os
import re

import argparse
from e2j2.helpers import templates
from e2j2.helpers.constants import BRIGHT_RED, RESET_ALL, GREEN, LIGHTGREEN, WHITE, YELLOW, DESCRIPTION


def arg_parse(program, description, version):
    arg_parser = argparse.ArgumentParser(prog=program, description=description)
    arg_parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s {}'.format(version))
    arg_parser.add_argument('-e', '--ext', '--extension',
                            default='.j2',
                            type=str,
                            help='Jinja2 file extension')
    arg_parser.add_argument('-f', '--filelist',
                            type=str,
                            help='Comma separated list of jinja2 templates')
    arg_parser.add_argument('-s', '--searchlist',
                            type=str,
                            help='Comma separated list of directories to search for jinja2 templates')
    arg_parser.add_argument('-N', '--noop',
                            action='store_true',
                            help="Only render the template, don't write to disk")
    arg_parser.add_argument('-r', '--recursive',
                            action='store_true',
                            help='Traverse recursively through the search list')
    arg_parser.add_argument('--no-color',
                            action='store_true',
                            help='Disable the use of ANSI color escapes')
    arg_parser.add_argument('-2', '--twopass',
                            action='store_true',
                            help='Enable two pass rendering')
    arg_parser.add_argument('--block_start',
                            type=str,
                            default='%{',
                            help="Block marker start (default: '{%%')")
    arg_parser.add_argument('--block_end',
                            type=str,
                            default='%}',
                            help="Block marker end (default: '%%}')")
    arg_parser.add_argument('--variable_start',
                            type=str,
                            default='{{',
                            help="Variable marker start (default: '{{')")
    arg_parser.add_argument('--variable_end',
                            type=str,
                            default='}}',
                            help="Variable marker start (default: '}}')")
    arg_parser.add_argument('--comment_start',
                            type=str,
                            default='#}',
                            help="Comment marker start (default: '{#')")
    arg_parser.add_argument('--comment_end',
                            type=str,
                            default='#}',
                            help="Comment marker end (default: '#}')")
    return arg_parser.parse_args()


def use_color(switch):
    if switch:
        bright_red = BRIGHT_RED
        green = GREEN
        lightgreen = LIGHTGREEN
        white = WHITE
        yellow = YELLOW
        reset_all = RESET_ALL
    else:
        bright_red, green, lightgreen, white, yellow, reset_all = ("",) * 6
    return bright_red, green, lightgreen, white, yellow, reset_all


def get_search_list(search_list):
    return search_list if search_list else os.environ.get('E2J2_SEARCHLIST', '.')


def get_files(**kwargs):
    if kwargs['filelist']:
        return kwargs['filelist'].split(',')
    else:
        return templates.find(searchlist=kwargs['searchlist'],
                              j2file_ext=kwargs['extension'], recurse=kwargs['recurse'])


def write_file(filename, content):
    with open(filename, mode='w') as fh:
        fh.writelines(content)


def e2j2():
    args = arg_parse('e2j2', DESCRIPTION, '0.1.15')

    search_list = get_search_list(args.searchlist)
    recursive = args.recursive
    extension = args.ext

    # initialize colors
    bright_red, green, lightgreen, white, yellow, reset_all = use_color(not args.no_color)

    j2vars = templates.get_vars()
    old_directory = ''

    j2files = get_files(filelist=args.filelist,  searchlist=search_list, extension=args.ext, recurse=recursive)

    directory = None
    for j2file in j2files:
        try:
            directory = os.path.dirname(j2file)
            filename = re.sub(r'{}$'.format(extension), '', j2file)

            if directory != old_directory:
                sys.stdout.write('\n{}In: {}{}\n'.format(green, white, directory))

            sys.stdout.write('    {}rendering: {}{:35}{} => '.format(green, white, os.path.basename(j2file), green))

            try:
                content = templates.render(
                    j2file=j2file,
                    j2vars=j2vars,
                    twopass=args.twopass,
                    block_start=args.block_start,
                    block_end=args.block_end,
                    variable_start=args.variable_start,
                    variable_end=args.variable_end,
                    comment_start=args.comment_start,
                    comment_end=args.comment_end)
                status = lightgreen + 'success' + reset_all
            except Exception as e:
                filename += '.err'
                content = str(e)
                status = bright_red + 'failed ' + reset_all

            sys.stdout.write('{}{:7} => writing: {}{:25}{} => '.format(status, green, white,
                                                                       os.path.basename(filename), green))

            if args.noop:
                sys.stdout.write('{}skipped{}\n'.format(yellow, reset_all))
            else:
                write_file(filename, content)
                sys.stdout.write('{}success{}\n'.format(lightgreen, reset_all))
        except Exception as e:
            sys.stdout.write('{}failed{} ({})\n'.format(bright_red, reset_all, str(e)))
        finally:
            old_directory = directory
            sys.stdout.flush()


if __name__ == '__main__':
    e2j2()
