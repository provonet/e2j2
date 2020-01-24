import os
import sys
import jinja2
import re
import json
import traceback
from jinja2.exceptions import TemplateNotFound, UndefinedError, FilterArgumentError, TemplateSyntaxError
from jsonschema import validate, ValidationError, draft4_format_checker
from e2j2.helpers.exceptions import E2j2Exception, JSONDecodeError
from e2j2.helpers.constants import RESET_ALL, YELLOW, CONFIG_SCHEMAS
from e2j2.tags import base64_tag, consul_tag, file_tag, json_tag, jsonfile_tag, list_tag, vault_tag, dns_tag
from e2j2.helpers import cache
from six import iteritems

try:
    from jinja2_ansible_filters import AnsibleCoreFiltersExtension
    j2_extensions = [AnsibleCoreFiltersExtension]
except ImportError:
    j2_extensions = []


def stdout(msg):
    print_at = cache.print_at
    increment = cache.increment
    counter = cache.log_repeat_log_msg_counter

    if cache.last_log_line != msg:
        sys.stdout.write(msg)
        cache.log_repeat_log_msg_counter = 0
    elif counter == print_at:
        sys.stdout.write('({}x) '.format(print_at) + msg)
        cache.print_at += increment
        cache.log_repeat_log_msg_counter = 0

    cache.log_repeat_log_msg_counter += 1
    cache.last_log_line = msg


def find(searchlist, j2file_ext, recurse=False):
    if recurse:
        return [os.path.realpath(os.path.join(dirpath, j2file)) for searchlist_item in searchlist
                for dirpath, dirnames, files in os.walk(searchlist_item, followlinks=True)
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
            if not defined_tag:
                envcontext[envvar] = envvalue
            else:
                tag_config, tag_value = parse_tag(config, defined_tag, envvalue)
                envcontext[envvar] = tag_value
                if 'flatten' in tag_config and tag_config['flatten'] and isinstance(tag_value, dict):
                    for key, value in iteritems(tag_value):
                        envcontext[key] = value

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
        # FIXME be more specific on raising error (config or data)
        try:
            tag_config = json.loads(envvars.get(config_var, '{}'))

            pattern = re.compile(r'config=([^}]+)}:(.+)')
            match = pattern.match(value)
            if match:
                tag_config = json.loads(match.group(1) + '}')
                value = match.group(2)

            if token_var in envvars:
                tag_config['token'] = tag_config['token'] if 'token' in tag_config else os.environ[token_var]

            if 'token' in tag_config and tag_config['token'].startswith('file:'):
                token_value = re.sub(r'^file:', '', tag_config['token'])
                tag_config['token'] = file_tag.parse(token_value).strip()

        except JSONDecodeError:
            raise E2j2Exception('decoding JSON failed')

        try:
            validate(instance=tag_config, schema=CONFIG_SCHEMAS[tag], format_checker=draft4_format_checker)
        except ValidationError:
            if config['stacktrace']:
                stdout(traceback.format_exc())

            raise E2j2Exception('config validation failed')

    if tag == 'json:':
        tag_value = json_tag.parse(value)
    elif tag == 'jsonfile:':
        tag_value = jsonfile_tag.parse(value)
    elif tag == 'base64:':
        tag_value = base64_tag.parse(value)
    elif tag == 'consul:':
        tag_value = consul_tag.parse(tag_config, value)
    elif tag == 'list:':
        tag_value = list_tag.parse(value)
    elif tag == 'file:':
        tag_value = file_tag.parse(value)
    elif tag == 'vault:':
        tag_value = vault_tag.parse(tag_config, value)
    elif tag == 'dns:':
        tag_value = dns_tag.parse(tag_config, value)
    else:
        return None, '** ERROR: tag: %s not implemented **' % tag

    return tag_config, tag_value


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
        comment_end_string=kwargs['comment_end'],
        extensions=j2_extensions)

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
