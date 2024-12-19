import sys

from . import build_start_times, run_gnome, build_cubes

# The keys in this dictionary are the names used in command line execution
# of code, e.g. `$ tapbuild start_times`
commands = {"start_times": build_start_times.build_start_times,
            "run_gnome": run_gnome.run_gnome,
            "build_cubes": build_cubes.build_cubes,
            }


def main():
    err_msg = ("You must pass in a command, and the path to a tap config file (python file)\n"
              f"Command options are: {[*commands]}\n"
              f"You passed: {sys.argv[1:]}")
    # note: use click or docopt to make this fancier?
    try:
        command = sys.argv[1].strip()
    except IndexError:
        print(err_msg)
        sys.exit()

    try:
        config_file = sys.argv[2]
    except IndexError:
        print(err_msg)
        sys.exit()

    try:
        cmd = commands[command]
    except KeyError:
        print(f"You must provide a valid command. You passed: {command}\n"
              f"Options are: {[*commands]}")
        sys.exit(1)

    cmd(config_file)
