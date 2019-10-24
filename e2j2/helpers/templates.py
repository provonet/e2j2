import os
import sys
import jinja2
import re
import json
from jsonschema import validate, ValidationError, draft4_format_checker
from deepmerge import always_merger
from e2j2.helpers.exception import E2j2Exception
from e2j2.helpers.constants import YELLOW, RESET_ALL, CONFIG_SCHEMAS
from e2j2.tags import base64_tag, consul_tag, file_tag, json_tag, jsonfile_tag, list_tag, vault_tag

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


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
    tags = ['json:', 'jsonfile:', 'base64:', 'consul:', 'list:', 'file:', 'vault:']
    envcontext = {}
    for envvar in env_list:
        envvalue = os.environ[envvar]
        defined_tag = ''.join([tag for tag in tags if envvalue.startswith(tag)])
        try:
            envcontext[envvar] = parse_tag(defined_tag, envvalue) if defined_tag else envvalue
        except E2j2Exception as e:
            stdout(YELLOW + "** WARNING: parsing {} failed with error: {} **".format(envvar, str(e)) + RESET_ALL + '\n')

    return envcontext


def parse_tag(tag, value):
    config = {}
    value = re.sub(r'^{}'.format(tag), '', value).strip()
    if tag in CONFIG_SCHEMAS:
        envvars = os.environ
        config_var = tag.upper()[:-1] + '_CONFIG'
        token_var = tag.upper()[:-1] + '_TOKEN'
        try:
            config = json.loads(envvars.get(config_var, '{}'))

            if token_var in envvars:
                config['token'] = os.environ[token_var]

            pattern = re.compile(r'config=([^}]+)}:(.+)')
            match = pattern.match(value)
            if match:
                tag_config = json.loads(match.group(1) + '}')
                config = always_merger.merge(config, tag_config)
                value = match.group(2)

        except JSONDecodeError:
            return '** ERROR: Decoding JSON **'

        try:
            validate(instance=config, schema=CONFIG_SCHEMAS[tag], format_checker=draft4_format_checker)
        except ValidationError:
            return '** ERROR: config validation failed **'

    if tag == 'json:':
        return json_tag.parse(value)
    elif tag == 'jsonfile:':
        return jsonfile_tag.parse(value)
    elif tag == 'base64:':
        return base64_tag.parse(value)
    elif tag == 'consul:':
        return consul_tag.parse(config, value)
    elif tag == 'list:':
        return list_tag.parse(value)
    elif tag == 'file:':
        return file_tag.parse(value)
    elif tag == 'vault:':
        return vault_tag.parse(config, value)
    else:
        return '** ERROR: tag: %s not implemented **' % tag


def render(**kwargs):
    path, filename = os.path.split(kwargs['j2file'])

    j2 = jinja2.Environment(
        loader=jinja2.FileSystemLoader([path or './', '/']),
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
