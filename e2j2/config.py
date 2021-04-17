import json
from simple_singleton import Singleton
from types import SimpleNamespace
from os import environ
from e2j2.exceptions import E2j2Exception


class Settings(metaclass=Singleton):
    extension = ".j2"
    recursive = False
    no_color = False
    twopass = False
    nested_tags = False
    stacktrace = False
    initial_run = False
    copy_file_permissions = False
    marker_set = "{{"
    autodetect_marker_set = False
    block_start = None
    block_end = None
    variable_start = None
    variable_end = None
    comment_start = None
    comment_end = None
    config_start = None
    config_end = None
    noop = False
    splay = 0
    run = []
    watchlist = []
    searchlist = []
    env_whitelist = []
    env_blacklist = []
    filelist = []


def add_entries(obj, data: dict):
    for key in data.keys():
        value = data[key]

        if isinstance(value, dict):
            setattr(obj, key, SimpleNamespace())
            add_entries(getattr(obj, key), value)
        else:
            setattr(obj, key, value)


def load_config(config_file: str):
    with open(config_file, "r") as fh:
        config = json.load(fh)

    settings = Settings()
    add_entries(settings, config)


def load_args(args):
    args_dict = {}
    [args_dict.update({key: value}) for key, value in vars(args).items() if value]
    settings = Settings()
    add_entries(settings, args_dict)

    settings.filelist = (
        args.filelist.split(",")
        if args.filelist
        else getattr(settings, "filelist", [])
    )

    env_searchlist = environ.get("E2J2_SEARCHLIST", ".").split(",")
    settings.searchlist = (
        args.searchlist.split(",")
        if args.searchlist
        else getattr(settings, "searchlist", env_searchlist)
    )

    settings.env_whitelist = (
        args.env_whitelist.split(",")
        if args.env_whitelist
        else getattr(settings, "env_whitelist", [])
    )

    settings.env_blacklist = (
        args.env_blacklist.split(",")
        if args.env_blacklist
        else getattr(settings, "env_blacklist", [])
    )

    settings.watchlist = (
        args.watchlist.split(",")
        if args.watchlist
        else getattr(settings, "watchlist", [])
    )

    if settings.initial_run and (not settings.watchlist or not settings.run):
        raise E2j2Exception("the following arguments are required: watchlist, run")
