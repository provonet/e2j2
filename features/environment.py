import requests
import subprocess
import os
import time
from zipfile import ZipFile
from behave.fixture import use_fixture, fixture


FNULL = open(os.devnull, 'w')


@fixture
def with_consul(_):
    consul_url = 'https://releases.hashicorp.com/consul/1.8.0/consul_1.8.0_linux_amd64.zip'
    resp = requests.get(consul_url, allow_redirects=True)
    open('/tmp/consul.zip', 'wb').write(resp.content)
    with ZipFile('/tmp/consul.zip', 'r') as archive:
        archive.extractall('/tmp')

    os.chmod('/tmp/consul', 0o755)

    consul = subprocess.Popen(['/tmp/consul', 'agent', '-dev'], stderr=FNULL, stdout=FNULL)
    time.sleep(10)
    try:
        yield consul
    finally:
        consul.kill()
        for file in ['/tmp/consul', '/tmp/consul.zip']:
            os.remove(file)
        time.sleep(2)


@fixture
def with_vault(_):
    vault_url = 'https://releases.hashicorp.com/vault/1.4.3/vault_1.4.3_linux_amd64.zip'
    resp = requests.get(vault_url, allow_redirects=True)
    open('/tmp/vault.zip', 'wb').write(resp.content)
    with ZipFile('/tmp/vault.zip', 'r') as archive:
        archive.extractall('/tmp')

    os.chmod('/tmp/vault', 0o755)

    vault = subprocess.Popen(['/tmp/vault', 'server', '-dev', '-dev-root-token-id', 'aabbccddeeff'], stderr=FNULL, stdout=FNULL)
    time.sleep(10)
    try:
        yield vault
    finally:
        vault.kill()
        for file in ['/tmp/vault', '/tmp/vault.zip']:
            os.remove(file)
        time.sleep(2)


def before_tag(context, tag):
    if tag == "fixture.with.consul":
        return use_fixture(with_consul, context)
    elif tag == "fixture.with.vault":
        return use_fixture(with_vault, context)
    else:
        raise ValueError('Unknown tag')
