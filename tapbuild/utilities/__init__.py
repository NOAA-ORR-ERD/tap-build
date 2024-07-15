
from datetime import datetime
import sys
import os
import importlib
from types import SimpleNamespace
import yaml


def import_from_path(module_name, file_path):
    """
    SourceFileLoader.load_module() is deprecated

    This is from a recipe in the docs.

    :param module_name: name the resulting module should have (internal __name__)

    :file_path: PathLike to the python file to load
    """
    file_path = os.fspath(file_path)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def load_config(config_file):
    """
    load the config file in the path given

    returns: an object with a namespace with configuration info

    Currently it can only load a python file, but could be extended in the future to load yaml, or ...

    NOTE: this could use `runpy.run_path()` and always get a dict.
    """
    config_file = os.fspath(config_file)

    if config_file[-3:] == ".py":
        config = import_from_path("config", config_file)
    elif config_file[-5:] == ".yaml":
        with open(config_file, encoding='utf-8') as infile:
            data = yaml.load(infile, Loader=yaml.Loader)
        config = SimpleNamespace(**data)
    else:
        raise ValueError(f"can only load Python (*.py) or yaml (*.yaml) files, not: {config_file}")

    return config


def read_start_times_file(filename, num_start_times):
    with open(filename) as stfile:
        start_dt = []
        for i in range(num_start_times):
        # get and parse start times in this season
            try:
                start_time = next(stfile)
            except StopIteration:
                raise ValueError("There are not enough times in the file.")
            start_time = [int(i) for i in start_time.split(',')]
            start_time = datetime(start_time[0],start_time[1],start_time[2],start_time[3],start_time[4])
            start_dt.append(start_time)
    return start_dt

