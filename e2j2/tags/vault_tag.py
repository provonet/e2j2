import requests
from requests.exceptions import RequestException
from urllib.parse import urlparse
from e2j2.constants import VAULT_STATUSCODES
from e2j2.exceptions import E2j2Exception


class Vault:
    def __init__(self, config):
        url = urlparse(config['url'] if 'url' in config else 'https://127.0.0.1:8200')
        if url.port:
            port = url.port
        else:
            port = 80 if url.scheme == 'http' else 443

        self.scheme = config['scheme'] if 'scheme' in config else url.scheme
        self.host = config['host'] if 'host' in config else url.hostname
        self.port = config['port'] if 'port' in config else port
        self.token = config['token'] if 'token' in config else None
        self.url = '%s://%s:%s/v1' % (self.scheme, self.host, self.port)
        self.session = self.setup()

    def setup(self):
        session = requests.session()
        session.headers.update({"Accept": "application/json"})
        session.headers.update({"X-Vault-Token": self.token})
        return session

    def get_raw(self, url):
        url = self.url + '/' + url
        try:
            response = self.session.get(url)
        except RequestException:
            raise E2j2Exception('failed to connect to %s' % url)

        if response.status_code == 200:
            return response.json()

        if str(response.status_code) in VAULT_STATUSCODES:
            raise E2j2Exception(VAULT_STATUSCODES[str(response.status_code)])

        raise E2j2Exception(response.status_code)

    def get_kv1(self, url):
        response = self.get_raw(url)
        # type is string so this will be an error
        if isinstance(response, str):
            return response

        return dict(response)['data']

    def get_kv2(self, url):
        parts = url.split('/')
        url = parts[0] + '/data/' + '/'.join(parts[1:])
        response = self.get_raw(url)
        # type is string so this will be an error
        if isinstance(response, str):
            return response

        return dict(response)['data']['data']


def parse(tag_config, value):
    vault = Vault(tag_config)

    if 'backend' not in tag_config or tag_config['backend'] == 'raw':
        return vault.get_raw(value)
    if tag_config['backend'] == 'kv1':
        return vault.get_kv1(value)
    elif tag_config['backend'] == 'kv2':
        return vault.get_kv2(value)
    else:
        raise E2j2Exception('Unknown K/V backend')
