import requests
import subprocess
import os
import time
from zipfile import ZipFile
from behave.fixture import use_fixture_by_tag


def with_consul(context):
    consul_url = 'https://releases.hashicorp.com/consul/1.8.0/consul_1.8.0_linux_amd64.zip'
    resp = requests.get(consul_url, allow_redirects=True)
    open('/tmp/consul.zip', 'wb').write(resp.content)
    with ZipFile('/tmp/consul.zip', 'r') as archive:
        archive.extractall('/tmp')

    os.chmod('/tmp/consul', 0o755)

    context.consul = subprocess.Popen(['/tmp/consul', 'agent', '-dev'])
    time.sleep(3)
    try:
        yield context.consul
    finally:
        context.consul.kill()
        for file in ['/tmp/consul', '/tmp/consul.zip']:
            os.remove(file)

fixture_registry = {
    "fixture.with.consul":  with_consul,
}


def before_tag(context, tag):
    if tag.startswith("fixture."):
        return use_fixture_by_tag(tag, context, fixture_registry)
