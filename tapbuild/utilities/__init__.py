
from datetime import datetime
import os
from importlib.machinery import SourceFileLoader
from types import SimpleNamespace
import yaml


def load_config(config_file):
    """
    load the config file in the path given

    returns: an object with a namespace with configuration info

    Currently it can only load a python file, but could be extended in the future to load yaml, or ...
    """
    config_file = os.fspath(config_file)

    if config_file[-3:] == ".py":
        config = SourceFileLoader("config", os.fspath(config_file)).load_module()
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

