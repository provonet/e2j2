import os
import sys
import jinja2
import re
import json
import traceback
from dpath import util as dpath_util
from jinja2.exceptions import UndefinedError, FilterArgumentError, TemplateSyntaxError
from jsonschema import validate, ValidationError, draft4_format_checker
from json.decoder import JSONDecodeError
from e2j2.exceptions import E2j2Exception
from e2j2.constants import RESET_ALL, YELLOW, CONFIG_SCHEMAS, TAGS, NESTED_TAGS, MARKER_SETS
from e2j2.tags import base64_tag, consul_tag, file_tag, json_tag, jsonfile_tag, list_tag, vault_tag, dns_tag, escape_tag
from e2j2 import cache

try:
    from jinja2_ansible_filters import AnsibleCoreFiltersExtension
    j2_extensions = [AnsibleCoreFiltersExtension]
except ImportError:
    j2_extensions = []


def recursive_iter(obj, keys=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from recursive_iter(v, keys + (k,))
    elif any(isinstance(obj, t) for t in (list, tuple)):
        for idx, item in enumerate(obj):
            yield from recursive_iter(item, keys + (idx,))
    else:
        yield keys, obj


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
    env_list = [entry for entry in whitelist if entry not in blacklist]
    envvars = os.environ
    return resolv_vars(config, env_list, envvars)


def resolv_vars(config, var_list, vars):
    # initialize colors
    yellow, reset_all = ("", "") if config['no_color'] else (YELLOW, RESET_ALL)

    varcontext = {}
    for var in var_list:
        var_value = vars[var]
        defined_tag = ''.join([tag for tag in TAGS if ':' in var_value and var_value.startswith(tag)])
        try:
            if not defined_tag:
                varcontext[var] = var_value
            else:
                tag_config, tag_value = parse_tag(config, defined_tag, var_value)
                varcontext[var] = tag_value

                if 'flatten' in tag_config and tag_config['flatten'] and isinstance(tag_value, dict):
                    for key, value in tag_value.items():
                        varcontext[key] = value

        except E2j2Exception as e:
            stdout(yellow + "** WARNING: parsing {} failed with error: {} **".format(var, str(e)) + reset_all + '\n')
    return varcontext


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
            pattern = re.compile(r'config=(.+)')
            match = pattern.match(value)

            markers = detect_markers(config, value)
            value_with_config = match.group(1).split(markers['config_end'] + ':') if pattern.match(value) else None

            if value_with_config and len(value_with_config) > 1:
                config_str, value = value_with_config
                config_str = config_str.lstrip(markers['config_start'])
                tag_config.update(json.loads('{%s}' % config_str))
            elif value_with_config:
                raise E2j2Exception("invalid config markers used, please place the config between the markers '%s' and '%s'" % (markers['config_start'], markers['config_end']))

            if token_var in envvars:
                tag_config['token'] = tag_config['token'] if 'token' in tag_config else envvars[token_var]

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
    elif tag == 'escape:':
        tag_value = escape_tag.parse(value)
    else:
        return None, '** ERROR: tag: %s not implemented **' % tag

    if config['twopass'] and tag in NESTED_TAGS:
        try:
            for keys, item in recursive_iter(tag_value):
                if isinstance(item, str):
                    dpath_util.set(tag_value, list(keys), resolv_vars(config, ['item'], {'item': item})['item'])
        except Exception:
            raise E2j2Exception('failed to resolve nested tag')

    return tag_config, tag_value


def render(config, j2file, j2vars):
    path, filename = os.path.split(j2file)
    j2 = jinja2.Environment(
        loader=jinja2.FileSystemLoader([path or './', '/']),
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
        extensions=j2_extensions)

    try:
        with open(j2file, 'r') as file:
            content = file.read()

        markers = detect_markers(config, content)
        j2.block_start_string = markers['block_start']
        j2.block_end_string = markers['block_end']
        j2.variable_start_string = markers['variable_start']
        j2.variable_end_string = markers['variable_end']
        j2.comment_start_string = markers['comment_start']
        j2.comment_end_string = markers['comment_end']
        first_pass = j2.from_string(content).render(j2vars)

        if config['twopass']:
            # second pass
            markers = detect_markers(config, first_pass)
            j2.block_start_string = markers['block_start']
            j2.block_end_string = markers['block_end']
            j2.variable_start_string = markers['variable_start']
            j2.variable_end_string = markers['variable_end']
            j2.comment_start_string = markers['comment_start']
            j2.comment_end_string = markers['comment_end']
            return j2.from_string(first_pass).render(j2vars)
        else:
            return first_pass
    except (UndefinedError, FilterArgumentError, TemplateSyntaxError) as err:
        exc_type, exc_value, exc_tb = sys.exc_info()
        stacktrace = traceback.format_exception(exc_type, exc_value, exc_tb)
        match = re.search(r'\sline\s(\d+)', stacktrace[-2])
        content = 'failed with error: {}'.format(err)
        content += ' at line: {}'.format(match.group(1)) if match else ''
        raise E2j2Exception(content)
    except FileNotFoundError:
        raise E2j2Exception('Template %s not found' % filename)
    except Exception as err:
        raise E2j2Exception(str(err))


def detect_markers(config, content):
    marker_set = MARKER_SETS[config['marker_set']]

    if config['autodetect_marker_set']:
        config_marker = True if 'config=' in content else False
        for key, value in MARKER_SETS.items():
            if config_marker:
                if 'config=' + MARKER_SETS[key]['config_start'] in content:
                    marker_set = MARKER_SETS[key]
            else:
                if MARKER_SETS[key]['variable_start'] in content and MARKER_SETS[key]['variable_end'] in content:
                    marker_set = MARKER_SETS[key]

    markers = {
        'block_start': config['block_start'] if config['block_start'] else marker_set['block_start'],
        'block_end': config['block_end'] if config['block_end'] else marker_set['block_end'],
        'variable_start': config['variable_start'] if config['variable_start'] else marker_set['variable_start'],
        'variable_end': config['variable_end'] if config['variable_end'] else marker_set['variable_end'],
        'comment_start': config['comment_start'] if config['comment_start'] else marker_set['comment_start'],
        'comment_end': config['comment_end'] if config['comment_end'] else marker_set['comment_end'],
        'config_start': config['config_start'] if config['config_start'] else marker_set['config_start'],
        'config_end': config['config_end'] if config['config_end'] else marker_set['config_end']}
    return markers
