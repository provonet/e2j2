import binascii
from base64 import b64decode


def parse(value):
    try:
        return b64decode(value).decode('utf-8')
    except (TypeError, binascii.Error):
        # Mark as failed
        return '** ERROR: decoding BASE64 string **'
