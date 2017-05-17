import sys
import os
import re

import click
from e2j2.helpers import templates
from e2j2.helpers.constants import ERROR, BRIGHT_RED, RESET_ALL, GREEN, LIGHTGREEN, WHITE, YELLOW

VERSION = '0.1.2'


@click.command()
@click.version_option(version=VERSION)
@click.option('-e', '--extention', default='.j2', help='Jinja2 file extention')
@click.option('-s', '--searchlist', help='Comma separated list of directories to search for jinja2 templates')
@click.option('-N', '--noop/--no-noop', default=False, help="Only render the template, don't write to disk")
@click.option('-r', '--recursive', is_flag=True, help='Traverse recursively through the search list')
def e2j2(searchlist, extention, noop, recursive):

    if not searchlist:
        searchlist = os.environ['E2J2_SEARCHLIST'] if 'E2J2_SEARCHLIST' in os.environ else '.'

    j2vars = templates.get_vars()
    old_directory = ''

    for j2file in templates.find(searchlist=searchlist, j2file_ext=extention, recurse=recursive):
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

            if noop:
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
