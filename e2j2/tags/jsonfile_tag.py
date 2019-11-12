import json
from e2j2.helpers.exceptions import E2j2Exception, JSONDecodeError


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
