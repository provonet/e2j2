def parse(file_name):
    try:
        with open(file_name) as file_handle:
            return file_handle.read()
    except IOError:
        # Mark as failed
        return '** ERROR: IOError raised while reading file **'
