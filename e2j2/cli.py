import sys
import re
import argparse
import os
import traceback
import json
import subprocess
from random import uniform as random_uniform
from subprocess import CalledProcessError
from threading import Thread
from time import sleep
from jsonschema import validate, draft4_format_checker
from os.path import basename
from stat import ST_MODE
from e2j2 import templates
from e2j2.templates import stdout, get_vars
from e2j2.constants import BRIGHT_RED, RESET_ALL, GREEN, LIGHTGREEN, WHITE, YELLOW, DESCRIPTION, VERSION
from e2j2.constants import CONFIG_SCHEMAS, MARKER_SETS
from e2j2.exceptions import E2j2Exception


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
                            help="Only render the templates, don't write to disk")
    arg_parser.add_argument('-r', '--recursive',
                            action='store_true',
                            help='Traverse recursively through the search list')
    arg_parser.add_argument('--no-color', '--nocolor', '--no_color',
                            action='store_true',
                            help='Disable the use of ANSI color escapes')
    arg_parser.add_argument('-2', '--twopass',
                            action='store_true',
                            help='Enable two pass rendering')
    arg_parser.add_argument('-m', '--marker-set',
                            type=str,
                            default='{{',
                            choices=['{{', '{=', '<=', '[=', '(='],
                            help="Select marker set")
    arg_parser.add_argument('-A', '--autodetect_marker_set',
                            action='store_true',
                            help='Autodetect marker set, fallback to marker set defined in --marker-set')
    arg_parser.add_argument('--block_start', '--block-start',
                            type=str,
                            help="Block marker start (default: use marker set)")
    arg_parser.add_argument('--block_end', '--block-end',
                            type=str,
                            help="Block marker end (default: use marker set)")
    arg_parser.add_argument('--variable_start', '--variable-start',
                            type=str,
                            help="Variable marker start (default: use marker set)")
    arg_parser.add_argument('--variable_end', '--variable-end',
                            type=str,
                            help="Variable marker start (default: use marker set)")
    arg_parser.add_argument('--comment_start', '--comment-start',
                            type=str,
                            help="Comment marker start (default: use marker set)")
    arg_parser.add_argument('--comment_end', '--comment-end',
                            type=str,
                            help="Comment marker end (default: use marker set)"),
    arg_parser.add_argument('--config-start',
                            type=str,
                            help="Config marker start (default: use marker set)")
    arg_parser.add_argument('--config-end',
                            type=str,
                            help="Config marker end (default: use marker set)")
    arg_parser.add_argument('-w', '--env_whitelist', '--env-whitelist',
                            type=str,
                            help="Include listed environment variables (default all)")
    arg_parser.add_argument('-b', '--env_blacklist', '--env-blacklist',
                            type=str,
                            help="Exclude listed environment variables (default none)")
    arg_parser.add_argument('-P', '--copy_file_permissions', '--copy-file-permissions',
                            action='store_true',
                            help='copy file permissions from template to rendered file'
                            )
    arg_parser.add_argument('-S', '--stacktrace',
                            action='store_true',
                        help='Include stack trace in error file / show stack trace'
                            )
    arg_parser.add_argument('-c', '--config',
                            type=str,
                            help='config file path'
                            )
    arg_parser.add_argument('--watchlist',
                            type=str,
                            help='watch listed environment variables for changes, and render template(s) on change'
                            )
    arg_parser.add_argument('--splay',
                            type=int,
                            default=0,
                            help='Random delay of watchlist polls (between 0 and 900 seconds)')
    arg_parser.add_argument('-R', '--run',
                            type=str,
                            help='run command after rendering template (command arg1 arg2 arg3)')
    arg_parser.add_argument('--initial_run', '--initial-run',
                            action='store_true',
                            help='Initial run after e2j2 (re)start')
    args = arg_parser.parse_args()

    if args.recursive and not args.searchlist and not 'E2J2_SEARCHLIST' in os.environ:
        arg_parser.error('the following arguments are required: searchlist')

    if args.splay and not args.watchlist:
        arg_parser.error('the following arguments are required: watchlist')

    if args.initial_run and (not args.watchlist or not args.run):
        arg_parser.error('the following arguments are required: watchlist, run')

    return args


def configure(args):
    config = {}
    if args.config:
        with open(args.config, 'r') as fh:
            config = json.load(fh)

    config['extension'] = args.ext if args.ext else config.get('extension', '.j2')
    config['filelist'] = args.filelist.split(',') if args.filelist else config.get('filelist', [])
    env_searchlist = os.environ.get('E2J2_SEARCHLIST', '.').split(',')
    config['searchlist'] = args.searchlist.split(',') if args.searchlist else config.get('searchlist', env_searchlist)
    config['recursive'] = args.recursive if args.recursive else config.get('recursive', False)
    config['no_color'] = args.no_color if args.no_color else config.get('no_color', False)
    config['twopass'] = args.twopass if args.twopass else config.get('twopass', False)
    config['stacktrace'] = args.stacktrace if args.stacktrace else config.get('stacktrace', False)
    config['initial_run'] = args.initial_run if args.initial_run else config.get('initial_run', False)
    config['copy_file_permissions'] = args.copy_file_permissions \
        if args.copy_file_permissions else config.get('copy_file_permissions', False)

    config['marker_set'] = args.marker_set if args.marker_set else config.get('marker_set', '{{')
    config['autodetect_marker_set'] = args.autodetect_marker_set if args.autodetect_marker_set else config.get('autodetect_marker_set', False)
    config['block_start'] = args.block_start if args.block_start else config.get('block_start', None)
    config['block_end'] = args.block_end if args.block_end else config.get('block_end', None)
    config['variable_start'] = args.variable_start if args.variable_start else config.get('variable_start', None)
    config['variable_end'] = args.variable_end if args.variable_end else config.get('variable_end', None)
    config['comment_start'] = args.comment_start if args.comment_start else config.get('comment_start', None)
    config['comment_end'] = args.comment_end if args.comment_end else config.get('comment_end', None)
    config['config_start'] = args.comment_start if args.comment_start else config.get('config_start', None)
    config['config_end'] = args.comment_end if args.comment_end else config.get('config_end', None)

    config['env_whitelist'] = args.env_whitelist.split(',') if args.env_whitelist else config.get('env_whitelist', [])
    config['env_blacklist'] = args.env_blacklist.split(',') if args.env_blacklist else config.get('env_blacklist', [])
    config['watchlist'] = args.watchlist.split(',') if args.watchlist else config.get('watchlist', [])
    config['splay'] = args.splay if args.watchlist else config.get('splay', 0)
    config['run'] = args.run.split() if args.run else config.get('run', [])
    config['noop'] = args.noop

    if config['initial_run'] and (not config['watchlist'] or not config['run']):
        raise E2j2Exception('the following arguments are required: watchlist, run')

    validate(instance=config, schema=CONFIG_SCHEMAS['configfile'], format_checker=draft4_format_checker)

    return config


def get_files(**kwargs):
    if kwargs['filelist']:
        return kwargs['filelist']
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


def run(config):
    exit_code = 0
    search_list = config['searchlist']
    recursive = config['recursive']
    extension = config['extension']

    # initialize colors
    bright_red, green, lightgreen, white, yellow, reset_all = ("",)*6 if config['no_color'] else \
        (BRIGHT_RED, GREEN, LIGHTGREEN, WHITE, YELLOW, RESET_ALL)

    env_whitelist = config['env_whitelist'] if config['env_whitelist'] else os.environ
    env_blacklist = config['env_blacklist'] if config['env_blacklist'] else []
    j2vars = templates.get_vars(config, whitelist=env_whitelist, blacklist=env_blacklist)
    old_directory = ''

    j2files = get_files(
        filelist=config['filelist'],  searchlist=search_list, extension=config['extension'], recurse=recursive)

    for j2file in j2files:
        try:
            directory = os.path.dirname(j2file)
            filename = re.sub(r'{}$'.format(extension), '', j2file)

            if directory != old_directory:
                stdout('\n{}In: {}{}\n'.format(green, white, directory))

            stdout('    {}rendering: {}{:35}{} => '.format(green, white, basename(j2file), green))

            try:
                content = templates.render(config, j2file, j2vars)
                status = lightgreen + 'success' + reset_all
            except Exception as err:
                exit_code = 1
                content = str(err)
                filename += '.err'
                status = bright_red + content + reset_all

                if config['stacktrace']:
                    content += "\n\n%s" % traceback.format_exc()

            stdout('{}{:7} => writing: {}{:25}{} => '.format(status, green, white, basename(filename), green))

            if config['noop']:
                stdout('{}skipped{}\n'.format(yellow, reset_all))
            else:
                write_file(filename, content)

                if config['copy_file_permissions']:
                    copy_file_permissions(j2file, filename)

                stdout('{}success{}\n'.format(lightgreen, reset_all))

        except Exception as err:
            stdout('{}failed{} ({})\n'.format(bright_red, reset_all, str(err)))
            exit_code = 1
        finally:
            sys.stdout.flush()

    if config['noop']:
        return exit_code

    if config['run']:
        command = ' '.join(config['run'])
        stdout('\n{0}Running:\n    command: {1}{2} {0} => {1}'.format(green, reset_all, command))

        if exit_code == 0:
            try:
                subprocess.check_output(config['run'], stderr=subprocess.STDOUT)
                stdout('{} done{}\n'.format(lightgreen, reset_all))
            except CalledProcessError as error:
                stdout('{} failed{}\n\n'.format(bright_red, reset_all))
                # FIXME only works on python > 3.4
                if hasattr(error, 'stdout'):
                    stdout('{}Output:{}\n'.format(bright_red, reset_all))
                    stdout(error.stdout.decode() + '\n')
                exit_code = 1
        else:
            stdout('{} skipped{}\n'.format(yellow, reset_all))

    return exit_code


def watch_run(config):
    bright_red, reset_all = ('', '') if config['no_color'] else (BRIGHT_RED, RESET_ALL)
    noop = config['noop']
    config['noop'] = True
    stdout('Changes detected, testing templates:\n')
    exit_code = run(config)

    if exit_code == 1:
        stdout('{}Test run failed, no changes applied{}'.format(bright_red, reset_all))
        return exit_code

    if noop:
        return exit_code

    stdout('\nApplying changes:\n')
    config['noop'] = False
    exit_code = run(config)
    return exit_code


def watch(config):
    old_env_data = None
    first_run = True
    cfg = config.copy()
    cfg['run'] = []
    bright_red, reset_all = ('', '') if config['no_color'] else (BRIGHT_RED, RESET_ALL)

    while True:
        try:
            env_data = get_vars(config, config['watchlist'], [])
        except KeyError as err:
            stdout('{}ERROR unknown key {} in watchlist{}\n'.format(bright_red, str(err), reset_all))
            break
        if old_env_data == env_data:
            try:
                sleep(random_uniform(1, config['splay']) if config['splay'] else 1)
                continue
            except KeyboardInterrupt:
                break

        if not config['initial_run'] and first_run:
            thread = Thread(target=watch_run, args=(cfg,))
        else:
            thread = Thread(target=watch_run, args=(config,))
        thread.start()

        old_env_data = env_data.copy()
        first_run = False


def e2j2():
    exit_code = 0
    args = arg_parse('e2j2', DESCRIPTION, VERSION)
    try:
        config = configure(args)
    except Exception as err:
        stdout('E2J2 configuration error: %s' % str(err))

        if args.stacktrace:
            stdout(traceback.format_exc())

        stdout('\n')
        exit_code = 1
        return exit_code
    if config['watchlist']:
        watch(config)
    else:
        exit_code = run(config)
    return exit_code
