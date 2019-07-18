import re


def parse(value):
    return re.split(r",\s*", value)
