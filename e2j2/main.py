import sys
import os
import re
import json
import jinja2
import click
from consul import Consul
from consul.base import ACLPermissionDenied
from colorama import Fore, Style
from base64 import b64decode


VERSION = '0.1.0'
ERROR = '**ERROR**'
BRIGHT_RED = Style.BRIGHT + Fore.RED
RESET_ALL = Style.RESET_ALL
YELLOW = Fore.YELLOW
GREEN = Fore.GREEN
LIGHTGREEN = Fore.LIGHTGREEN_EX
WHITE = Fore.WHITE


def find_j2files(searchlist, j2file_ext, recurse=False):
    if recurse:
        return [os.path.realpath(os.path.join(dirpath, j2file)) for searchlist_item in searchlist.split(',')
                for dirpath, dirnames, files in os.walk(searchlist_item)
                for j2file in files if j2file.endswith(j2file_ext)]
    else:
        return [os.path.realpath(os.path.join(searchlist_item, j2file)) for searchlist_item in searchlist.split(',')
                for j2file in os.listdir(searchlist_item) if j2file.endswith(j2file_ext)]


def parse_json_string(json_string):
    try:
        return json.loads(json_string)
    except ValueError:
        # Mark as failed
        return ERROR


def parse_json_file(json_file):
    try:
        with open(json_file) as json_file:
            data = json.load(json_file)
    except IOError:
        # Mark as failed
        return ERROR

    return data


def parse_base64(value):
    try:
        return b64decode(value)
    except TypeError:
        # Mark as failed
        return ERROR


def parse_consul(value):
    consul_config = json.loads(os.environ['CONSUL_CONFIG']) if 'CONSUL_CONFIG' in os.environ else {}

    scheme = consul_config['scheme'] if 'scheme' in consul_config else 'http'
    host = consul_config['host'] if 'host' in consul_config else '127.0.0.1'
    port = consul_config['port'] if 'port' in consul_config else 8500
    token = consul_config['token'] if 'token' in consul_config else None

    try:
        consul = Consul(scheme=scheme, host=host, port=port, token=token)
        _, kv_entries = consul.kv.get(recurse=True, key=value)
    except ACLPermissionDenied:
        print(BRIGHT_RED + 'Access denied connecting to: {}://{}:{}'.format(scheme, host, port) + RESET_ALL)
        return ERROR

    if not kv_entries:
        # Mark as failed if we can't find the consul key
        return ERROR

    flattend = {}
    for entry in kv_entries:
        # strip 'root' key from value, and store subkeys as keys in the returned dict
        # deeper nested keys will be stored in the form subkey_key or subkey_subsubkey_key, ..
        key = entry['Key'].replace(value + '/', '').replace('/', '_')
        flattend[key] = entry['Value']

    return flattend[value] if value in flattend else flattend


def parse_tag(tag, value):
    # strip tag from value
    value = re.sub(r'^{}'.format(tag), '', value).strip()
    if tag == 'json:':
        return parse_json_string(value)
    elif tag == 'jsonfile:':
        return parse_json_file(value)
    elif tag == 'base64:':
        return parse_base64(value)
    elif tag == 'consul:':
        return parse_consul(value)
    else:
        raise KeyError('tag: {} not implemented')


def j2vars_from_environment():
    tags = ['json:', 'jsonfile:', 'base64:', 'consul:']
    envcontext = {}
    for envvar in os.environ:
        envvalue = os.environ[envvar]
        defined_tag = [tag for tag in tags if envvalue.startswith(tag)]
        envcontext[envvar] = parse_tag(defined_tag[0], envvalue) if defined_tag else envvalue
    return envcontext


def render_template(j2file, j2vars):
    path, filename = os.path.split(j2file)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(j2vars)


@click.command()
@click.version_option(version=VERSION)
@click.option('-e', '--extention', default='.j2', help='Jinja2 file extention')
@click.option('-s', '--searchlist', help='Comma separated list of directories to search for jinja2 templates')
@click.option('-N', '--noop/--no-noop', default=False, help="Only render the template, don't write to disk")
@click.option('-r', '--recursive', is_flag=True, help='Traverse recursively through the search list')
def e2j2(searchlist, extention, noop, recursive):

    if not searchlist:
        searchlist = os.environ['E2J2_SEARCHLIST'] if 'E2J2_SEARCHLIST' in os.environ else '.'

    j2vars = j2vars_from_environment()
    old_directory = ''

    for j2file in find_j2files(searchlist=searchlist, j2file_ext=extention, recurse=recursive):
        try:
            directory = os.path.dirname(j2file)
            filename = re.sub(r'{}$'.format(extention), '', j2file)

            if directory != old_directory:
                sys.stdout.write('\n{}In: {}{}\n'.format(GREEN, WHITE, os.path.dirname(j2file)))

            sys.stdout.write('    {}rendering: {}{:35}{} => '.format(GREEN, WHITE, os.path.basename(j2file), GREEN))

            try:
                rendered_file = render_template(j2file=j2file, j2vars=j2vars)
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
