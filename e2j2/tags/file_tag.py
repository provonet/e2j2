from e2j2.helpers.exceptions import E2j2Exception


def parse(file_name):
    try:
        # print(file_name)
        with open(file_name) as file_handle:
            return file_handle.read()
    except IOError:
        # Mark as failed
        raise E2j2Exception('IOError raised while reading file: %s' % file_name)
