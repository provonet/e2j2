VERSION = '0.6.0'
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
boolean = {'type': 'boolean'}

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
          'test_first': {'type': 'boolean'},
          'copy_file_permissions': {'type': 'boolean'},
          'stacktrace': {'type': 'boolean'},
          'initial_run': {'type': 'boolean'},
          'marker_set': {'type': 'string', 'enum': ['{{', '{=', '<=', '[=', '(=']},
          'autodetect_marker_set': {'type': 'boolean'},
          'block_start': {'type': ['string', 'null']},
          'block_end': {'type': ['string', 'null']},
          'variable_start': {'type': ['string', 'null']},
          'variable_end': {'type': ['string', 'null']},
          'comment_start': {'type': ['string', 'null']},
          'comment_end': {'type': ['string', 'null']},
          'config_start': {'type': ['string', 'null']},
          'config_end': {'type': ['string', 'null']},
          'splay': {'type': 'number', 'minimum': 0, 'maximum': 900}
      },
      "additionalProperties":   False
    },
    'json:': {
      'type': 'object',
      'properties': {
            'flatten': boolean
      }
    },
    'jsonfile:': {
        'type': 'object',
        'properties': {
            'flatten': boolean
        }
    },
    'consul:': {
        'type': 'object',
        'properties': {
            'url': uri,
            'scheme': scheme,
            'host': host,
            'port': port,
            'token': token,
            'flatten': boolean
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
            'flatten': boolean
        },
        "additionalProperties":   False
    },
    'dns:': {
        'type': 'object',
        'properties': {
            'nameservers': {'type': 'array', 'items': {'type': 'string',
                                                       'oneOf': [{'format': 'ipv4'}, {'format': 'ipv6'}]}},
            'port': port,
            'type': {'type': 'string', 'enum': ['A', 'AAAA', 'MX', 'SRV']},
            'flatten': boolean
        },
        "additionalProperties": False
    }
}

TAGS = ['json:', 'jsonfile:', 'base64:', 'consul:', 'list:', 'file:', 'vault:', 'dns:', 'escape:']
NESTED_TAGS = ['json:', 'jsonfile:', 'list:']
MARKER_SETS = {
    "{{":{
        'block_start': '{%', 'block_end': '%}',
        'variable_start': '{{', 'variable_end': '}}',
        'comment_start': '{#', 'comment_end': '#}',
        'config_start': '{', 'config_end': '}'
    },
    "{=": {
        'block_start': '<%', 'block_end': '%>',
        'variable_start': '{=', 'variable_end': '=}',
        'comment_start': '<#', 'comment_end': '#>',
        'config_start': '<', 'config_end': '>'
    },
    "<=": {
        'block_start': '<%', 'block_end': '%>',
        'variable_start': '<=', 'variable_end': '=>',
        'comment_start': '<#', 'comment_end': '#>',
        'config_start': '<', 'config_end': '>'
    },
    "[=": {
        'block_start': '[%', 'block_end': '%]',
        'variable_start': '[=', 'variable_end': '=]',
        'comment_start': '[#', 'comment_end': '#]',
        'config_start': '[', 'config_end': ']'
    },
    "(=": {
        'block_start': '(%', 'block_end': '%)',
        'variable_start': '(=', 'variable_end': '=)',
        'comment_start': '(#', 'comment_end': '#)',
        'config_start': '(', 'config_end': ')'
    }
}
