import json


try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def parse(json_file):
    try:
        with open(json_file) as json_file:
            data = json.load(json_file)
    except IOError:
        # Mark as failed
        return '** ERROR: IOError raised while reading file **'
    except JSONDecodeError:
        return '** Error: Decoding JSON **'

    return data