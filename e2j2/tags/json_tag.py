import json
import re

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def parse(json_string):
    try:
        # handle hashrocket styled json
        if re.search('"\s*=>\s*["{[]', json_string):
            return json.loads(re.sub('"\s*=>\s*', '":', json_string))
        else:
            return json.loads(json_string)
    except JSONDecodeError:
        return '** ERROR: Decoding JSON **'
