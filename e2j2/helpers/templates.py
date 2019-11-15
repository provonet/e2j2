import os
import sys
import jinja2
import re
import json
import traceback
from jinja2.exceptions import TemplateNotFound, UndefinedError, FilterArgumentError, TemplateSyntaxError
from jsonschema import validate, ValidationError, draft4_format_checker
from deepmerge import always_merger
from e2j2.helpers.exceptions import E2j2Exception, JSONDecodeError
from e2j2.helpers.constants import RESET_ALL, YELLOW, CONFIG_SCHEMAS
from e2j2.tags import base64_tag, consul_tag, file_tag, json_tag, jsonfile_tag, list_tag, vault_tag, dns_tag
from e2j2.helpers import cache


def stdout(msg):
    display_every = cache.log_display_every
    increment = 5
    counter = cache.log_repeat_log_msg_counter

    if cache.last_log_line != msg:
        sys.stdout.write(msg)
        cache.log_repeat_log_msg_counter = 1
    elif counter // display_every == counter / display_every:
        sys.stdout.write('({}x) '.format(display_every) + msg)
        cache.log_display_every += increment
        cache.log_repeat_log_msg_counter = 1

    cache.log_repeat_log_msg_counter += 1
    cache.last_log_line = msg


def find(searchlist, j2file_ext, recurse=False):
    if recurse:
        return [os.path.realpath(os.path.join(dirpath, j2file)) for searchlist_item in searchlist
                for dirpath, dirnames, files in os.walk(searchlist_item)
                for j2file in files if j2file.endswith(j2file_ext)]
    else:
        return [os.path.realpath(os.path.join(searchlist_item, j2file)) for searchlist_item in searchlist
                for j2file in os.listdir(searchlist_item) if j2file.endswith(j2file_ext)]


def get_vars(config, whitelist, blacklist):
    # initialize colors
    yellow, reset_all = ("", "") if config['no_color'] else (YELLOW, RESET_ALL)

    env_list = [entry for entry in whitelist if entry not in blacklist]
    tags = ['json:', 'jsonfile:', 'base64:', 'consul:', 'list:', 'file:', 'vault:', 'dns:']
    envcontext = {}
    for envvar in env_list:
        envvalue = os.environ[envvar]
        defined_tag = ''.join([tag for tag in tags if ':' in envvalue and envvalue.startswith(tag)])
        try:
            envcontext[envvar] = parse_tag(config, defined_tag, envvalue) if defined_tag else envvalue
        except E2j2Exception as e:
            stdout(yellow + "** WARNING: parsing {} failed with error: {} **".format(envvar, str(e)) + reset_all + '\n')

    return envcontext


def parse_tag(config, tag, value):
    tag_config = {}
    value = re.sub(r'^{}'.format(tag), '', value).strip()
    if tag in CONFIG_SCHEMAS:
        envvars = os.environ
        config_var = tag.upper()[:-1] + '_CONFIG'
        token_var = tag.upper()[:-1] + '_TOKEN'
        try:
            tag_config = json.loads(envvars.get(config_var, '{}'))

            if token_var in envvars:
                tag_config['token'] = os.environ[token_var]

            pattern = re.compile(r'config=([^}]+)}:(.+)')
            match = pattern.match(value)
            if match:
                tag_config = json.loads(match.group(1) + '}')
                tag_config = always_merger.merge(tag_config, tag_config)
                value = match.group(2)

        except JSONDecodeError:
            raise E2j2Exception('decoding JSON failed')

        try:
            validate(instance=tag_config, schema=CONFIG_SCHEMAS[tag], format_checker=draft4_format_checker)
        except ValidationError:
            if config['stacktrace']:
                stdout(traceback.format_exc())

            raise E2j2Exception('config validation failed')

    if tag == 'json:':
        return json_tag.parse(value)
    elif tag == 'jsonfile:':
        return jsonfile_tag.parse(value)
    elif tag == 'base64:':
        return base64_tag.parse(value)
    elif tag == 'consul:':
        return consul_tag.parse(tag_config, value)
    elif tag == 'list:':
        return list_tag.parse(value)
    elif tag == 'file:':
        return file_tag.parse(value)
    elif tag == 'vault:':
        return vault_tag.parse(tag_config, value)
    elif tag == 'dns:':
        return dns_tag.parse(tag_config, value)
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

    try:
        first_pass = j2.get_template(filename).render(kwargs['j2vars'])
        if kwargs['twopass']:
            # second pass
            return j2.from_string(first_pass).render(kwargs['j2vars'])
        else:
            return first_pass
    except (UndefinedError, FilterArgumentError, TemplateSyntaxError) as err:
        exc_type, exc_value, exc_tb = sys.exc_info()
        stacktrace = traceback.format_exception(exc_type, exc_value, exc_tb)
        match = re.search(r'\sline\s(\d+)', stacktrace[-2])
        content = 'failed with error: {}'.format(err)
        content += ' at line: {}'.format(match.group(1)) if match else ''
        raise E2j2Exception(content)
    except TemplateNotFound:
        raise E2j2Exception('Template %s not found' % filename)
    except Exception as err:
        raise E2j2Exception(str(err))
