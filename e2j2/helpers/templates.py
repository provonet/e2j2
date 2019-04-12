import os
import re
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


def render(j2file, j2vars, twopass=False):
    path, filename = os.path.split(j2file)

    if twopass:
        with open(j2file, 'r') as file:
            template = file.read()

            # add extra raw tags for 2nd pass
            template = re.sub(r'(\{%\s*raw\s*%\})', r'\1%%%RAW%%%', template, flags=re.IGNORECASE)
            template = re.sub(r'(\{%\s*endraw\s*%\})', r'\1%%%ENDRAW%%%', template, flags=re.IGNORECASE)

            # first pass
            template = jinja2.Environment(
                loader=jinja2.BaseLoader(), keep_trailing_newline=True).from_string(template).render(j2vars)

            # re insert raw tags
            template = re.sub(r'%%%RAW%%%', r'{% raw %}', template)
            template = re.sub(r'%%%ENDRAW%%%', r'{% endraw %}', template)

            # second pass
            return jinja2.Environment(
                loader=jinja2.BaseLoader(), keep_trailing_newline=True).from_string(template).render(j2vars)
    else:
        return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './'),
                                  keep_trailing_newline=True,
                                  undefined=jinja2.StrictUndefined).get_template(filename).render(j2vars)
