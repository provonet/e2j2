import sys
import re
import argparse
import os
import traceback
from os.path import basename
from stat import ST_MODE
from e2j2.helpers import templates
from e2j2.helpers.templates import stdout
from e2j2.helpers.constants import BRIGHT_RED, RESET_ALL, GREEN, LIGHTGREEN, WHITE, YELLOW, DESCRIPTION, VERSION


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
                            default='{%',
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
                            default='{#',
                            help="Comment marker start (default: '{#')")
    arg_parser.add_argument('--comment_end',
                            type=str,
                            default='#}',
                            help="Comment marker end (default: '#}')")
    arg_parser.add_argument('-w', '--env_whitelist',
                            type=str,
                            help="Include listed environment variables (default all)")
    arg_parser.add_argument('-b', '--env_blacklist',
                            type=str,
                            help="Exclude listed environment variables (default none)")
    arg_parser.add_argument('-P', '--copy_file_permissions',
                            action='store_true',
                            help='copy file permissions from template to rendered file'
                            )
    arg_parser.add_argument('-S', '--stacktrace',
                            action='store_true',
                            help='Include stacktrace in error file'
                            )
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


def copy_file_permissions(source, destination):
    stat = os.stat(source)

    # set ownership
    os.chown(destination, stat.st_uid, stat.st_gid)
    # set permissions
    perm = oct(stat[ST_MODE] & 0o777)
    os.chmod(destination, int(perm, 8))


def write_file(filename, content):
    with open(filename, mode='w') as fh:
        fh.writelines(content)


def e2j2():
    exit_code = 0
    args = arg_parse('e2j2', DESCRIPTION, VERSION)

    search_list = get_search_list(args.searchlist)
    recursive = args.recursive
    extension = args.ext

    # initialize colors
    bright_red, green, lightgreen, white, yellow, reset_all = use_color(not args.no_color)

    env_whitelist = args.env_whitelist.split(',') if args.env_whitelist else os.environ
    env_blacklist = args.env_blacklist.split(',') if args.env_blacklist else []
    j2vars = templates.get_vars(whitelist=env_whitelist, blacklist=env_blacklist)
    old_directory = ''

    j2files = get_files(filelist=args.filelist,  searchlist=search_list, extension=args.ext, recurse=recursive)

    for j2file in j2files:
        try:
            directory = os.path.dirname(j2file)
            filename = re.sub(r'{}$'.format(extension), '', j2file)

            if directory != old_directory:
                stdout('\n{}In: {}{}\n'.format(green, white, directory))

            stdout('    {}rendering: {}{:35}{} => '.format(green, white, basename(j2file), green))

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

                exc_type, exc_value, exc_tb = sys.exc_info()
                stacktrace = traceback.format_exception(exc_type, exc_value, exc_tb)
                match = re.search(r'\sline\s(\d+)', stacktrace[-2])

                if match:
                    content = 'failed with error: {} at line: {}'.format(str(e), match.group(1))
                    status = bright_red + 'failed with error: {} at line: {}'.format(str(e), match.group(1)) + reset_all
                else:
                    content = str(e)
                    status = bright_red + 'failed with error: {}'.format(str(e)) + reset_all

                if args.stacktrace:
                    content += "\n\n%s" % traceback.format_exc()

                exit_code = 1

            stdout('{}{:7} => writing: {}{:25}{} => '.format(status, green, white, basename(filename), green))

            if args.noop:
                stdout('{}skipped{}\n'.format(yellow, reset_all))
            else:
                write_file(filename, content)

                if args.copy_file_permissions:
                    copy_file_permissions(j2file, filename)

                stdout('{}success{}\n'.format(lightgreen, reset_all))

        except Exception as e:
            stdout('{}failed{} ({})\n'.format(bright_red, reset_all, str(e)))
            exit_code = 1
        finally:
            sys.stdout.flush()
    return exit_code
