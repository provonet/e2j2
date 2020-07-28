import binascii
from base64 import b64decode
from e2j2.exceptions import E2j2Exception


def parse(value):
    try:
        return b64decode(value).decode('utf-8')
    except (TypeError, binascii.Error):
        # Mark as failed
        raise E2j2Exception('invalid BASE64 string')
