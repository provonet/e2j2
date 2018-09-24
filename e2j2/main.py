import sys
import os
import re

import argparse
from e2j2.helpers import templates
from e2j2.helpers.constants import ERROR, BRIGHT_RED, RESET_ALL, GREEN, LIGHTGREEN, WHITE, YELLOW, DESCRIPTION


def e2j2():

    arg_parser = argparse.ArgumentParser(prog='e2j2', description=DESCRIPTION)
    arg_parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s 0.1.10')
    arg_parser.add_argument('-e', '--ext', '--extention',
                            default='.j2',
                            type=str,
                            help='Jinja2 file extention')
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

    args = arg_parser.parse_args()

    searchlist = args.searchlist if args.searchlist else os.environ.get('E2J2_SEARCHLIST', '.')
    recursive = args.recursive
    extention = args.ext

    # initialize colors
    use_color = False if args.no_color else True

    if use_color:
        bright_red = BRIGHT_RED
        green = GREEN
        lightgreen = LIGHTGREEN
        white = WHITE
        yellow = YELLOW
        reset_all = RESET_ALL
    else:
        bright_red, reset_all, green, lightgreen, white, yellow, reset_all = ("",) * 7

    j2vars = templates.get_vars()
    old_directory = ''

    j2files = args.filelist.split(',') if args.filelist else \
        templates.find(searchlist=searchlist, j2file_ext=args.ext, recurse=recursive)

    for j2file in j2files:
        try:
            directory = os.path.dirname(j2file)
            filename = re.sub(r'{}$'.format(extention), '', j2file)

            if directory != old_directory:
                sys.stdout.write('\n{}In: {}{}\n'.format(green, white, os.path.dirname(j2file)))

            sys.stdout.write('    {}rendering: {}{:35}{} => '.format(green, white, os.path.basename(j2file), green))

            try:
                rendered_file = templates.render(j2file=j2file, j2vars=j2vars)
                status = lightgreen + 'success' + reset_all
            except Exception as e:
                filename += '.err'
                rendered_file = str(e)
                status = bright_red + 'failed ' + reset_all

            sys.stdout.write('{}{:7} => writing: {}{:25}{} => '.format(status, green, white,
                                                                       os.path.basename(filename), green))

            if args.noop:
                sys.stdout.write('{}skipped{}\n'.format(yellow, reset_all))
            else:
                with open(filename, mode='w') as fh:
                    fh.writelines(rendered_file)
                sys.stdout.write('{}success{}\n'.format(lightgreen, reset_all))
        except Exception as e:
            sys.stdout.write('{}failed{} ({})\n'.format(bright_red, reset_all, str(e)))
        finally:
            old_directory = directory
            sys.stdout.flush()


if __name__ == '__main__':
    e2j2()
