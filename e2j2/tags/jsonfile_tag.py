import json
from json.decoder import JSONDecodeError
from e2j2.exceptions import E2j2Exception


def parse(json_file):
    try:
        with open(json_file) as json_file:
            data = json.load(json_file)
    except IOError:
        # Mark as failed
        raise E2j2Exception('IOError raised while reading file')
    except JSONDecodeError:
        raise E2j2Exception ('invalid JSON')

    return data
