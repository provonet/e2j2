import json
import os
import re
import binascii
import operator
from consul import Consul
from consul.base import ACLPermissionDenied
from functools import reduce
from base64 import b64decode
from deepmerge import Merger


try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class ConsulKV:
    def __init__(self, config):
        self.scheme = config['scheme'] if 'scheme' in config else 'http'
        self.host = config['host'] if 'host' in config else '127.0.0.1'
        self.port = config['port'] if 'port' in config else 8500
        self.token = config['token'] if 'token' in config else None
        self.client = self.setup()

    def setup(self):
        return Consul(scheme=self.scheme, host=self.host, port=self.port, token=self.token)

    def get(self, key, recurse=False):
        _, entries = self.client.kv.get(recurse=recurse, key=key)
        return entries


def parse_json_string(json_string):
    try:
        # handle hashrocket styled json
        if re.search('"\s*=>\s*["{[]', json_string):
            return json.loads(re.sub('"\s*=>\s*', '":', json_string))
        else:
            return json.loads(json_string)
    except JSONDecodeError:
        # Mark as failed
        return '** ERROR: Decoding JSON **'


def parse_json_file(json_file):
    try:
        with open(json_file) as json_file:
            data = json.load(json_file)
    except IOError:
        # Mark as failed
        return '** ERROR: IOError raised while reading file **'
    except JSONDecodeError:
        return '** Error: Decoding JSON **'

    return data


def parse_base64(value):
    try:
        return b64decode(value).decode('utf-8')
    except (TypeError, binascii.Error):
        # Mark as failed
        return '** ERROR: decoding BASE64 string **'


def parse_consul(consul_key):
    try:
        env = os.environ
        consul_config = json.loads(env['CONSUL_CONFIG']) if 'CONSUL_CONFIG' in env else {}
    except JSONDecodeError:
        # Mark as failed
        return '** ERROR: parsing consul_config **'

    consul_kv = ConsulKV(config=consul_config)
    consul_merger = Merger([(list, ['append']), (dict, ['merge'])], ['override'], ['override'])
    consul_key = consul_key.rstrip('/')

    try:
        kv_entries = consul_kv.get(recurse=True, key=consul_key)
    except ACLPermissionDenied:
        return '** Access denied connecting to: {}://{}:{} **'.format(consul_kv.scheme, consul_kv.host, consul_kv.port)

    if not kv_entries:
        # Mark as failed if we can't find the consul key
        return '** ERROR: Key not found **'
    consul_dict = {}
    for entry in kv_entries:
        subkeys = entry['Key'].split('/')
        value = entry['Value'].decode('utf-8') if hasattr(entry['Value'], 'decode') else entry['Value']
        value = '' if value is None else value
        if '/' in entry['Key']:
            key = '{"' + entry['Key'].replace('/', '":{"') + '": "' + value + '"}'.ljust(len(subkeys)+1, '}')
            consul_dict = consul_merger.merge(consul_dict, json.loads(key))
        else:
            consul_dict[entry['Key']] = value
    return reduce(operator.getitem, consul_key.split('/'), consul_dict)


def parse_list(value):
    return re.split(r",\s*", value)


def parse_file(file_name):
    try:
        with open(file_name) as file_handle:
            return file_handle.read()
    except IOError:
        # Mark as failed
        return '** ERROR: IOError raised while reading file **'


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
    elif tag == 'list:':
        return parse_list(value)
    elif tag == 'file:':
        return parse_file(value)
    else:
        return '** ERROR: tag: %s not implemented **' % tag
