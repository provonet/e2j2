import sys
import os
import re

import argparse
from e2j2.helpers import templates
from e2j2.helpers.constants import ERROR, BRIGHT_RED, RESET_ALL, GREEN, LIGHTGREEN, WHITE, YELLOW, DESCRIPTION

VERSION = '0.1.3'


def e2j2():

    arg_parser = argparse.ArgumentParser(prog='e2j2', description=DESCRIPTION)
    arg_parser.add_argument('-e', '--ext', '--extention',
                            default='.j2',
                            type=str,
                            help='Jinja2 file extention')
    arg_parser.add_argument('-s', '--searchlist',
                            type=str,
                            help='Comma separated list of directories to search for jinja2 templates')
    arg_parser.add_argument('-N', '--noop',
                            action='store_true',
                            help="Only render the template, don't write to disk")
    arg_parser.add_argument('-r', '--recursive',
                            action='store_true',
                            help='Traverse recursively through the search list')

    args = arg_parser.parse_args()

    searchlist = args.searchlist if args.searchlist else os.environ.get('E2J2_SEARCHLIST', '.')
    recursive = args.recursive
    extention = args.ext

    j2vars = templates.get_vars()
    old_directory = ''

    for j2file in templates.find(searchlist=searchlist, j2file_ext=args.ext, recurse=recursive):
        try:
            directory = os.path.dirname(j2file)
            filename = re.sub(r'{}$'.format(extention), '', j2file)

            if directory != old_directory:
                sys.stdout.write('\n{}In: {}{}\n'.format(GREEN, WHITE, os.path.dirname(j2file)))

            sys.stdout.write('    {}rendering: {}{:35}{} => '.format(GREEN, WHITE, os.path.basename(j2file), GREEN))

            try:
                rendered_file = templates.render(j2file=j2file, j2vars=j2vars)
                status = LIGHTGREEN + 'success' + RESET_ALL
            except Exception as e:
                filename += '.err'
                rendered_file = str(e)
                status = BRIGHT_RED + 'failed ' + RESET_ALL

            if ERROR in rendered_file:
                # template contains error so we will write content to filename.failed
                filename += '.err'
                status = BRIGHT_RED + 'failed ' + RESET_ALL

            sys.stdout.write('{}{:7} => writing: {}{:25}{} => '.format(status, GREEN, WHITE,
                                                                       os.path.basename(filename), GREEN))

            if args.noop:
                sys.stdout.write('{}skipped{}\n'.format(YELLOW, RESET_ALL))
            else:
                with open(filename, mode='w') as fh:
                    fh.writelines(rendered_file)
                sys.stdout.write('{}success{}\n'.format(LIGHTGREEN, RESET_ALL))
        except Exception as e:
            sys.stdout.write('{}failed{} ({})\n'.format(BRIGHT_RED, RESET_ALL, str(e)))
        finally:
            old_directory = directory
            sys.stdout.flush()


if __name__ == '__main__':
    e2j2()
