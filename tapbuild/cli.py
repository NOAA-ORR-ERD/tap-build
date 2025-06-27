import sys

from . import (build_start_times,
               run_gnome,
               build_cubes,
               build_site)

# The keys in this dictionary are the names used in command line execution
# of code, e.g. `$ tapbuild start_times`
commands = {"start_times": build_start_times.build_start_times,
            "run_gnome": run_gnome.run_gnome,
            "build_cubes": build_cubes.build_cubes,
            "build_site": build_site.build_site,
            }

HELP = ("tapbuild CMD CONFIG_file\n\n"
        "You must pass in a command and the path to a tap config"
        "file (python or yaml file)\n\n"
        f"Command options are: {[*commands]}\n\n"
        "You passed: {}")


def main():
    err_msg = HELP.format(sys.argv[1:])
    # note: use click or docopt to make this fancier?
    try:
        command = sys.argv[1].strip()
    except IndexError:
        print(err_msg)
        sys.exit()
    if command not in commands:
        print(err_msg)
        sys.exit()

    try:
        config_file = sys.argv[2]
    except IndexError:
        print(err_msg)
        sys.exit()

    try:
        tapbuild_function = commands[command]
    except KeyError:
        print(f"You must provide a valid command. You passed: {command}\n"
              f"Options are: {[*commands]}")
        sys.exit(1)

    tapbuild_function(config_file)
