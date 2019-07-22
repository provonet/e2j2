import requests
import subprocess
from six.moves.urllib.parse import urlparse
from e2j2.helpers.constants import VAULT_STATUSCODES

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


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
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()

        if str(response.status_code) in VAULT_STATUSCODES:
            return '** ERROR: {} **'.format(VAULT_STATUSCODES[str(response.status_code)])

        return '** ERROR: {} **'.format(response.status_code)

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


def parse(config, value):
    print(config)
    if 'token_script' in config and 'token' in config:
        return '** ERROR use token or token_script not both **'

    if 'token_script' in config:
        token_script = config['token_script']

        try:
            token_script = [token_script] if isinstance(token_script, str) else token_script
            token = subprocess.check_output(token_script).decode('utf-8').rstrip()
        except (FileNotFoundError, IOError):
            return '** ERROR: script: %s not found **' % token_script[0]
        except Exception as err:
            return '** ERROR %s raised **' % str(err)

        config['token'] = token
        del config["token_script"]

    vault = Vault(config)

    if 'backend' not in config or config['backend'] == 'raw':
        return vault.get_raw(value)
    if config['backend'] == 'kv1':
        return vault.get_kv1(value)
    elif config['backend'] == 'kv2':
        return vault.get_kv2(value)
    else:
        return '** ERROR: Unknown backend **'
