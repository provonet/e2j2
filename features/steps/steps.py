import pkg_resources
import os
import subprocess
import re
import requests
import json
from behave import step


@step('an installed {} module')
def pip_modules(context, module_name):
    installed_modules = [p.project_name for p in pkg_resources.working_set]
    assert module_name in installed_modules


@step('I set the environment {} variable to {}')
def set_envvar(context, envvar, value):
    os.environ[envvar] = value


@step('I create a template {} with the following content')
@step('I create a file {} with the following content')
def write_template(context, template_file):
    with open(template_file, 'w') as fh:
        fh.write(context.text)

    context.template_file = template_file


@step('I render the template with e2j2')
def render_template(context):
    FNULL = open(os.devnull, 'w')
    subprocess.call(['e2j2', '-f', context.template_file], stdout=FNULL)


@step('I render the template with e2j2 with additional flags {}')
@step('I render the template with e2j2 with additional flag {}')
def render_template(context, flags):
    flag_list = ['e2j2', '-f', context.template_file]
    flag_list.extend(flags.split(' '))
    FNULL = open(os.devnull, 'w')
    subprocess.call(flag_list, stdout=FNULL)


@step('rendered content is as follows')
def read_file(context):
    filename = re.sub(r'\.j2$', '', context.template_file)
    with open(filename, 'r') as fh:
        content = fh.read()

    # print(content)
    # print(context.text)
    assert content == context.text


@step("I PUT '{payload}' to '{url}' with headers '{headers}'")
def put_to_url(context, payload, url, headers):
    session = requests.put(url, data=payload, headers=json.loads(headers))
    context.statuscode = session.status_code
    context.body = session.text


@step("I POST '{payload}' to '{url}' with headers '{headers}'")
def post_to_url(context, payload, url, headers):
    try:
        session = requests.post(url, json=json.loads(payload), headers=json.loads(headers))
    finally:
        session = requests.post(url, data=payload, headers=json.loads(headers))
    context.statuscode = session.status_code
    context.body = session.text
