import json
import re
from e2j2.helpers.exception import E2j2Exception

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
        raise E2j2Exception('invalid JSON')
