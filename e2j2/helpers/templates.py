import os
import sys
import jinja2
from e2j2.helpers.constants import BRIGHT_RED, RESET_ALL
from e2j2.helpers import parsers


def stdout(msg):
    sys.stdout.write(msg)


def find(searchlist, j2file_ext, recurse=False):
    if recurse:
        return [os.path.realpath(os.path.join(dirpath, j2file)) for searchlist_item in searchlist.split(',')
                for dirpath, dirnames, files in os.walk(searchlist_item)
                for j2file in files if j2file.endswith(j2file_ext)]
    else:
        return [os.path.realpath(os.path.join(searchlist_item, j2file)) for searchlist_item in searchlist.split(',')
                for j2file in os.listdir(searchlist_item) if j2file.endswith(j2file_ext)]


def get_vars(whitelist, blacklist):
    env_list = [entry for entry in whitelist if entry not in blacklist]
    tags = ['json:', 'jsonfile:', 'base64:', 'consul:', 'list:', 'file:']
    envcontext = {}
    for envvar in env_list:
        envvalue = os.environ[envvar]
        defined_tag = [tag for tag in tags if envvalue.startswith(tag)]
        envcontext[envvar] = parsers.parse_tag(defined_tag[0], envvalue) if defined_tag else envvalue

        if '** ERROR:' in envcontext[envvar]:
            stdout(BRIGHT_RED + "{}='{}'".format(envvar, envcontext[envvar]) + RESET_ALL + '\n')

    return envcontext


def render(**kwargs):
    path, filename = os.path.split(kwargs['j2file'])

    j2 = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './'),
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
        block_start_string=kwargs['block_start'],
        block_end_string=kwargs['block_end'],
        variable_start_string=kwargs['variable_start'],
        variable_end_string=kwargs['variable_end'],
        comment_start_string=kwargs['comment_start'],
        comment_end_string=kwargs['comment_end'])

    first_pass = j2.get_template(filename).render(kwargs['j2vars'])
    if kwargs['twopass']:
        # second pass
        return j2.from_string(first_pass).render(kwargs['j2vars'])
    else:
        return first_pass
