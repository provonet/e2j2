import json
import operator
from consul import Consul
from consul.base import ACLPermissionDenied
from functools import reduce
from deepmerge import Merger
from urllib.parse import urlparse
from json.decoder import JSONDecodeError
from e2j2.exceptions import E2j2Exception


class ConsulKV:
    def __init__(self, config):
        url = urlparse(config['url'] if 'url' in config else 'http://127.0.0.1:8500')
        if url.port:
            port = url.port
        else:
            port = 80 if url.scheme == 'http' else 443

        self.scheme = config['scheme'] if 'scheme' in config else url.scheme
        self.host = config['host'] if 'host' in config else url.hostname
        self.port = config['port'] if 'port' in config else port
        self.token = config['token'] if 'token' in config else None
        self.url = '%s://%s:%s/v1' % (self.scheme, self.host, self.port)
        self.client = self.setup()

    def setup(self):
        return Consul(scheme=self.scheme, host=self.host, port=self.port, token=self.token)

    def get(self, key, recurse=False):
        _, entries = self.client.kv.get(recurse=recurse, key=key)
        return entries


def parse(tag_config, value):

    consul_kv = ConsulKV(config=tag_config)
    consul_merger = Merger([(list, ['append']), (dict, ['merge'])], ['override'], ['override'])
    consul_key = value.rstrip('/')

    try:
        kv_entries = consul_kv.get(recurse=True, key=consul_key)
    except ACLPermissionDenied:
        raise E2j2Exception('access denied connecting to: {}://{}:{} **'.format(consul_kv.scheme, consul_kv.host, consul_kv.port))
    except AssertionError as err:
        raise E2j2Exception(err)

    if not kv_entries:
        # Mark as failed if we can't find the consul key
        raise E2j2Exception('key not found')
    consul_dict = {}
    try:
        for entry in kv_entries:
            subkeys = entry['Key'].split('/')
            value = entry['Value'].decode('utf-8') if hasattr(entry['Value'], 'decode') else entry['Value']
            value = '' if value is None else value
            value = value.replace('"', '\\"')  # escape double quotes
            value = value.replace('\n', '\\n')  # escape newlines
            if '/' in entry['Key']:
                key = '{"' + entry['Key'].replace('/', '":{"') + '": "' + value + '"}'.ljust(len(subkeys)+1, '}')
                consul_dict = consul_merger.merge(consul_dict, json.loads(key))
            else:
                consul_dict[entry['Key']] = value
        return reduce(operator.getitem, consul_key.split('/'), consul_dict)
    except JSONDecodeError as err:
        raise E2j2Exception(err)
