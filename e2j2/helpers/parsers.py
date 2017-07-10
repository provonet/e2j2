import json
import os
import re
from consul import Consul
from consul.base import ACLPermissionDenied
from base64 import b64decode
from e2j2.helpers.constants import ERROR, BRIGHT_RED, RESET_ALL
from deepmerge import Merger


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
        return b64decode(value).decode('utf-8')
    except TypeError:
        # Mark as failed
        return ERROR


def parse_consul(value):
    consul_config = json.loads(os.environ['CONSUL_CONFIG']) if 'CONSUL_CONFIG' in os.environ else {}

    scheme = consul_config['scheme'] if 'scheme' in consul_config else 'http'
    host = consul_config['host'] if 'host' in consul_config else '127.0.0.1'
    port = consul_config['port'] if 'port' in consul_config else 8500
    token = consul_config['token'] if 'token' in consul_config else None

    consul_merger = Merger([(list, ['append']), (dict, ['merge'])], ['override'], ['override'])

    try:
        consul = Consul(scheme=scheme, host=host, port=port, token=token)
        _, kv_entries = consul.kv.get(recurse=True, key=value)
    except ACLPermissionDenied:
        print(BRIGHT_RED + 'Access denied connecting to: {}://{}:{}'.format(scheme, host, port) + RESET_ALL)
        return ERROR

    if not kv_entries:
        # Mark as failed if we can't find the consul key
        return ERROR
    consul_dict = {}
    for entry in kv_entries:
        subkeys = entry['Key'].split('/')
        value = entry['Value'].decode('utf-8') if hasattr(entry['Value'], 'decode') else entry['Value']
        if '/' in entry['Key']:
            key = '{"' + entry['Key'].replace('/', '":{"') + '": "' + value + '"}'.ljust(len(subkeys)+1, '}')
            consul_dict = consul_merger.merge(consul_dict, json.loads(key))
        else:
            consul_dict[entry['Key']] = value

    # return subkeys relative to rootkey
    rootkey = list(consul_dict.keys())[0]
    return consul_dict[rootkey]


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
