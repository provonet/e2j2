VERSION = '0.4.2'
ERROR = '** ERROR'
BRIGHT_RED = '\033[1;31m'
RESET_ALL = '\033[00m'
YELLOW = '\033[93m'
GREEN = '\033[0;32m'
LIGHTGREEN = '\033[1;32m'
WHITE = '\033[0;37m'
DESCRIPTION = 'Parse jinja2 templates with enhanced JSON aware environment variables'
VAULT_STATUSCODES = {
    '200': 'Success',
    '204': 'Success, no data',
    '400': 'Invalid request',
    '403': 'Forbidden',
    '404': 'Path not found',
    '500': 'Internal server error',
    '503': 'Sealed'
}
uri = {'type': 'string', 'format': 'uri'}
scheme = {'type': 'string', 'enum': ['http', 'https']}
host = {'type': 'string', 'format': 'hostname'}
port = {'type': 'number', 'minimum': 0, 'maximum': 65535}
token = {'type': 'string', "minLength": 5}
# fixme ipv6 support
ip = {'type': 'string', 'format': 'ipv4'}

CONFIG_SCHEMAS = {
    'configfile': {
      'type': 'object',
      'properties': {
          'extension': {'type': 'string'},
          'filelist': {'type': 'array', 'items': {'type': 'string'}},
          'searchlist': {'type': 'array', 'items': {'type': 'string'}},
          'env_whitelist': {'type': 'array', 'items': {'type': 'string'}},
          'env_blacklist': {'type': 'array', 'items': {'type': 'string'}},
          'watchlist': {'type': 'array', 'items': {'type': 'string'}},
          'run': {'type': 'array', 'items': {'type': 'string'}},
          'recursive': {'type': 'boolean'},
          'no_color': {'type': 'boolean'},
          'twopass': {'type': 'boolean'},
          'noop': {'type': 'boolean'},
          'copy_file_permissions': {'type': 'boolean'},
          'stacktrace': {'type': 'boolean'},
          'block_start': {'type': 'string'},
          'block_end': {'type': 'string'},
          'variable_start': {'type': 'string'},
          'variable_end': {'type': 'string'},
          'comment_start': {'type': 'string'},
          'comment_end': {'type': 'string'}
      },
      "additionalProperties":   False
    },
    'consul:': {
        'type': 'object',
        'properties': {
            'url': uri,
            'scheme': scheme,
            'host': host,
            'port': port,
            'token': token,
        },
        "additionalProperties":   False
    },
    'vault:': {
        'type': 'object',
        'properties': {
            'url': uri,
            'scheme': scheme,
            'host': host,
            'port': port,
            'token': token,
            'backend': {'type': 'string', 'enum': ['raw', 'kv1', 'kv2']},
        },
        "additionalProperties":   False
    },
    'dns:': {
        'type': 'object',
        'properties': {
            'nameservers': {'type': 'array', 'items': ip},
            'port': port,
            'type': {'type': 'string', 'enum': ['A', 'AAAA', 'MX', 'SRV']}
        },
        "additionalProperties": False
    }
}
