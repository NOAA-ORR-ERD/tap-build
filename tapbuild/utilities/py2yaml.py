#!/usr/bin/env python
"""
Convert a Python file into a yaml file.

Not really robust, but should do the basics.

What it does is simply make a dict out of the global namespace and dump it.

must be run as a top-level script -- i.e. not installed

NOTE: you need to make sure the current working dir is the same as the
      one the python file is in, so relative paths will work.

"""

from importlib.machinery import SourceFileLoader
from pathlib import Path, PosixPath
import sys
from types import ModuleType

import yaml

# code to convert Path objects to strings when writing yaml
from os import fspath

def path_as_str(dumper, path):
    return dumper.represent_str(fspath(path))

yaml.add_multi_representer(PosixPath, path_as_str)

infile = sys.argv[1]

outfile = infile[:-3] + ".yaml"

config = SourceFileLoader("config", infile).load_module()

def is_dumpable(name, obj):
    """
    returns True is the object is reasonable to dump into the yaml file
    """
    if (name.startswith("_")
        or isinstance(obj, ModuleType)
        or isinstance(obj, type)
        ):
        return False
    else:
        return True

DATA = {name: obj for name, obj in vars(config).items() if is_dumpable(name, obj)}

# for key, obj in DATA.items():
#     print(key, type(obj))

yaml.dump(DATA, open(outfile, 'w'))

