from e2j2.exceptions import E2j2Exception


def parse(file_name):
    try:
        with open(file_name) as file_handle:
            return file_handle.read()
    except IOError:
        # Mark as failed
        raise E2j2Exception('IOError raised while reading file: %s' % file_name)
