try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class E2j2Exception(Exception):
    pass
