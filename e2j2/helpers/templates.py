import os
import jinja2
from e2j2.helpers.constants import BRIGHT_RED, RESET_ALL
from e2j2.helpers import parsers


def find(searchlist, j2file_ext, recurse=False):
    if recurse:
        return [os.path.realpath(os.path.join(dirpath, j2file)) for searchlist_item in searchlist.split(',')
                for dirpath, dirnames, files in os.walk(searchlist_item)
                for j2file in files if j2file.endswith(j2file_ext)]
    else:
        return [os.path.realpath(os.path.join(searchlist_item, j2file)) for searchlist_item in searchlist.split(',')
                for j2file in os.listdir(searchlist_item) if j2file.endswith(j2file_ext)]


def get_vars():
    tags = ['json:', 'jsonfile:', 'base64:', 'consul:', 'list:', 'file:']
    envcontext = {}
    for envvar in os.environ:
        envvalue = os.environ[envvar]
        defined_tag = [tag for tag in tags if envvalue.startswith(tag)]
        envcontext[envvar] = parsers.parse_tag(defined_tag[0], envvalue) if defined_tag else envvalue

        if '** ERROR:' in envcontext[envvar]:
            print(BRIGHT_RED + "{}='{}'".format(envvar, envcontext[envvar]) + RESET_ALL)

    return envcontext


def render(j2file, j2vars):
    path, filename = os.path.split(j2file)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './'),
        undefined=jinja2.StrictUndefined).get_template(filename).render(j2vars)
