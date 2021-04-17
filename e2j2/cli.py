import sys
import re
import argparse
import os
import traceback
import subprocess
from random import uniform as random_uniform
from subprocess import CalledProcessError
from threading import Thread
from time import sleep
from os.path import basename
from stat import ST_MODE
from e2j2 import templates
from e2j2.templates import get_vars
from e2j2.constants import DESCRIPTION, VERSION
from e2j2.config import Settings, load_config, load_args
from e2j2.display import (
    no_colors,
    write,
    get_colors,
)

settings = Settings()


def arg_parse(program, description, version):
    arg_parser = argparse.ArgumentParser(prog=program, description=description)
    arg_parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s {}".format(version)
    )
    arg_parser.add_argument(
        "-e",
        "--extension",
        "--ext",
        type=str,
        help="Jinja2 file extension",
    )
    arg_parser.add_argument(
        "-f", "--filelist", type=str, help="Comma separated list of jinja2 templates"
    )
    arg_parser.add_argument(
        "-s",
        "--searchlist",
        type=str,
        help="Comma separated list of directories to search for jinja2 templates",
    )
    arg_parser.add_argument(
        "-N",
        "--noop",
        action="store_true",
        help="Only render the templates, don't write to disk",
    )
    arg_parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Traverse recursively through the search list",
    )
    arg_parser.add_argument(
        "--no-color",
        "--nocolor",
        "--no_color",
        action="store_true",
        help="Disable the use of ANSI color escapes",
    )
    arg_parser.add_argument(
        "-2", "--twopass", action="store_true", help="Enable two pass rendering"
    )
    arg_parser.add_argument(
        "-n",
        "--nested-tags",
        action="store_true",
        help="Enable support for nested tags (tags within json:, jsonfile: and list: tags)",
    )
    arg_parser.add_argument(
        "-m",
        "--marker-set",
        type=str,
        default="{{",
        choices=["{{", "{=", "<=", "[=", "(="],
        help="Select marker set",
    )
    arg_parser.add_argument(
        "-A",
        "--autodetect-marker-set",
        "--autodetect_marker_set",
        action="store_true",
        help="Autodetect marker set, fallback to defined marker set",
    )
    arg_parser.add_argument(
        "--block-start",
        "--block_start",
        type=str,
        help="Block marker start (default: use marker set)",
    )
    arg_parser.add_argument(
        "--block-end",
        "--block_end",
        type=str,
        help="Block marker end (default: use marker set)",
    )
    arg_parser.add_argument(
        "--variable-start",
        "--variable_start",
        type=str,
        help="Variable marker start (default: use marker set)",
    )
    arg_parser.add_argument(
        "--variable-end",
        "--variable_end",
        type=str,
        help="Variable marker start (default: use marker set)",
    )
    arg_parser.add_argument(
        "--comment-start",
        "--comment_start",
        type=str,
        help="Comment marker start (default: use marker set)",
    )
    arg_parser.add_argument(
        "--comment-end",
        "--comment_end",
        type=str,
        help="Comment marker end (default: use marker set)",
    ),
    arg_parser.add_argument(
        "--config-start", type=str, help="Config marker start (default: use marker set)"
    )
    arg_parser.add_argument(
        "--config-end", type=str, help="Config marker end (default: use marker set)"
    )
    arg_parser.add_argument(
        "-w",
        "--env-whitelist",
        "--env_whitelist",
        type=str,
        help="Include listed environment variables (default all)",
    )
    arg_parser.add_argument(
        "-b",
        "--env-blacklist",
        "--env_blacklist",
        type=str,
        help="Exclude listed environment variables (default none)",
    )
    arg_parser.add_argument(
        "-P",
        "--copy-file-permissions",
        "--copy_file_permissions",
        action="store_true",
        help="copy file permissions from template to rendered file",
    )
    arg_parser.add_argument(
        "-S",
        "--stacktrace",
        action="store_true",
        help="Include stack trace in error file / show stack trace",
    )
    arg_parser.add_argument("-c", "--config", type=str, help="config file path")
    arg_parser.add_argument(
        "--watchlist",
        type=str,
        help="watch listed environment variables for changes, and render template(s) on change",
    )
    arg_parser.add_argument(
        "--splay",
        type=int,
        default=0,
        help="Random delay of watchlist polls (between 0 and 900 seconds)",
    )
    arg_parser.add_argument(
        "-R",
        "--run",
        nargs=argparse.REMAINDER,
        help="run command after rendering template (command arg1 ...)",
    )
    arg_parser.add_argument(
        "--initial-run",
        "--initial_run",
        action="store_true",
        help="Initial run after e2j2 (re)start",
    )
    args = arg_parser.parse_args()

    if args.recursive and not args.searchlist and not "E2J2_SEARCHLIST" in os.environ:
        arg_parser.error("the following arguments are required: searchlist")

    if args.splay and not args.watchlist:
        arg_parser.error("the following arguments are required: watchlist")

    if args.initial_run and (not args.watchlist or not args.run):
        arg_parser.error("the following arguments are required: watchlist, run")

    return args


def get_files(**kwargs):
    if kwargs["filelist"]:
        return kwargs["filelist"]
    else:
        return templates.find(
            searchlist=kwargs["searchlist"],
            j2file_ext=kwargs["extension"],
            recurse=kwargs["recurse"],
        )


def copy_file_permissions(source, destination):
    stat = os.stat(source)

    # set ownership
    os.chown(destination, stat.st_uid, stat.st_gid)
    # set permissions
    perm = oct(stat[ST_MODE] & 0o777)
    os.chmod(destination, int(perm, 8))


def write_file(filename, content):
    with open(filename, mode="w") as fh:
        fh.writelines(content)


def run():
    colors = get_colors()
    exit_code = 0
    search_list = settings.searchlist
    recursive = settings.recursive
    extension = settings.extension

    j2vars = templates.get_vars(
        whitelist=settings.env_whitelist, blacklist=settings.env_blacklist
    )
    old_directory = ""

    j2files = get_files(
        filelist=settings.filelist,
        searchlist=search_list,
        extension=settings.extension,
        recurse=recursive,
    )

    for j2file in j2files:
        try:
            directory = os.path.dirname(j2file)
            filename = re.sub(r"{}$".format(extension), "", j2file)

            if directory != old_directory:
                write(
                    f"\n{colors.green}In:{'':1}{colors.white}{directory}{colors.reset}\n"
                )

            write(
                f"{'':3}{colors.green}rendering:{'':1}{colors.white}{basename(j2file):35}{'':1}{colors.green}=>{'':1}"
            )

            try:
                content = templates.render(j2file, j2vars)
                status = f"{colors.green}success"
            except Exception as err:
                exit_code = 1
                content = str(err)
                filename += ".err"
                status = f"{colors.green}content"

                if settings.stacktrace:
                    content += "\n\n%s" % traceback.format_exc()

            write(
                f"{status:7}{'':1}{colors.green}=> writing{'':1}{colors.white}{basename(filename):35}{'':1}{colors.green}=>{'':1}"
            )

            if settings.noop:
                write(f"{colors.yellow}skipped{colors.reset}\n")
            else:
                write_file(filename, content)

                if settings.copy_file_permissions:
                    copy_file_permissions(j2file, filename)

                write(f"{colors.green}success{colors.reset}\n")

        except Exception as err:
            write(f"{colors.red}failed{colors.reset}{'':1}({str(err)})\n")
            exit_code = 1
        finally:
            sys.stdout.flush()

    if settings.noop:
        return exit_code

    if settings.run:
        command = " ".join(settings.run)
        write(
            f"\n{colors.green}Running:{colors.reset}\n{'':3}command:{'':1}{command}{'':1}{colors.green}=>"
        )

        if exit_code == 0:
            try:
                result = subprocess.check_output(
                    settings.run, stderr=subprocess.STDOUT
                )
                write(f"{colors.lightgreen}{'':1}done${colors.reset}\n")
                write(f"{colors.green}Output:{colors.reset}\n")
                write(f"{result.decode()}\n")
            except CalledProcessError as error:
                write(f"{colors.red}{'':1}failed{colors.reset}\n\n")
                if hasattr(error, "stdout"):
                    write(f"{colors.red}Output:{colors.reset}\n")
                    write(f"{error.stdout.decode()}\n")
                exit_code = 1
        else:
            write(f"{colors.yellow}{'':1}skipped{colors.reset}\n")

    return exit_code


# def watch_run(config):
#     colors = get_colors()
#     noop = config["noop"]
#     config["noop"] = True
#     write("Changes detected, testing templates:\n")
#     exit_code = run(config)
#
#     if exit_code == 1:
#         write(f"{colors.red}Test run failed, no changes applied${colors.reset}")
#         return exit_code
#
#     if noop:
#         return exit_code
#
#     write("\nApplying changes:\n")
#     config["noop"] = False
#     exit_code = run(config)
#     return exit_code


def watch():
    ...
#     colors = get_colors()
#     old_env_data = None
#     first_run = True
#     cfg = config.copy()
#     cfg["run"] = []
#
#     while True:
#         try:
#             env_data = get_vars(config, config["watchlist"], [])
#         except KeyError as err:
#             write(
#                 f"{colors.red}ERROR unknown key {str(err)} in watchlist{colors.reset}\n"
#             )
#             break
#         if old_env_data == env_data:
#             try:
#                 sleep(random_uniform(1, config["splay"]) if config["splay"] else 1)
#                 continue
#             except KeyboardInterrupt:
#                 break
#
#         if not config["initial_run"] and first_run:
#             thread = Thread(target=watch_run, args=(cfg,))
#         else:
#             thread = Thread(target=watch_run, args=(config,))
#         thread.start()
#
#         old_env_data = env_data.copy()
#         first_run = False


def e2j2():
    exit_code = 0
    args = arg_parse("e2j2", DESCRIPTION, VERSION)
    try:
        if args.config:
            load_config(args.config)

        load_args(args)

        if settings.no_color:
            no_colors()

    except Exception as err:
        write(f"E2J2 configuration error: {str(err)}")

        if args.stacktrace:
            write(traceback.format_exc())

        write("\n")
        exit_code = 1
        return exit_code
    if settings.watchlist:
        watch()
    else:
        exit_code = run()
    return exit_code
