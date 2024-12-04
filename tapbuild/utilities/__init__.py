
from datetime import datetime
import sys
import os
import importlib
from types import SimpleNamespace
import yaml

# Added with coast_trader code merge
import calendar
import numpy as np
import random

# for build_grid class
import math

# imports used in file_map
import gridded # to get time variable in "file_map"
import xarray as xr
import netCDF4 as nc
import pandas as pd
from glob import glob
from pathlib import Path

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

def BuildGrid(Grid,min_lat, max_lat, min_lon, max_lon, lat_spacing, lon_spacing):
    """
    Returns Grid with number of lat/lon cells needed to create specified grid spacing (km)
    """
    #def build_grid(min_lat, max_lat, min_lon, max_lon, lat_spacing, lon_spacing):

    # general constants
    lat_dist = 111.325 # km in 1 degree latitude
    earth_radius = 6378 #km

    # Grid assignments
    Grid.min_lat = min_lat
    Grid.max_lat = max_lat
    Grid.min_long = min_lon
    Grid.max_long = max_lon

    # Grid spacing in latitude direction
    N_km_lat = lat_spacing  # grid distance (km) in lat direction
    Ncells_lat = lat_dist * (Grid.max_lat - Grid.min_lat) / N_km_lat
    Grid.dlat = (Grid.max_lat - Grid.min_lat) / Ncells_lat

    # Grid spacing in longitude direction
    N_km_lon = lon_spacing  # grid distance (km) in lon direction
    lat_radian = math.radians((Grid.max_lat - Grid.min_lat)/2)
    lon_dist = lat_dist * math.cos(lat_radian)
    Ncells_lon = lon_dist * (Grid.max_long - Grid.min_long) / N_km_lon
    Grid.dlong = (Grid.max_long - Grid.min_long) / Ncells_lon

    # Grid elements in lat/lon directions
    Grid.num_lat = int(
        np.ceil(np.abs(Grid.max_lat - Grid.min_lat)/Grid.dlat) + 1
    )
    Grid.num_long = int(
        np.ceil(np.abs(Grid.max_long - Grid.min_long)/Grid.dlong) + 1
    )

# This script is same as what is used in main
def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        if len(os.listdir(path)) > 0:
            print(f"Keeping existing files and adding to directory.")

def WriteStartTimes(Seasons,RootDir,TrajectoryDuration, NumStarts):
    """
     WriteStartTimes is a modified version of BuildStartTimes
     It does not account for time gaps
     It does not include a check to see if the start times have files
    """

    print(f"---Building Start Times ---")
    for season, month, year in Seasons:

        # set flag to check for missing files
        check_incomplete = True

        # Find start times
        # randomly generate NumStarts within range, up to the end of
        # season minus the run time
        RunTime = timedelta(hours = TrajectoryDuration)
        StartTimes = []

        for starts in np.arange(NumStarts):
            RandomYear = random.randrange(year[0],year[1]+1)
            RandomMonth = random.choices(month)[0]
            last_day_of_month = (
                calendar.monthrange(RandomYear, RandomMonth)[1]
            )
            RandomDay = random.randrange(
                1, last_day_of_month
            )
            StartHour = random.randrange(0,24)
            date = datetime(
                    year = RandomYear,
                    month = RandomMonth,
                    day = RandomDay,
                    hour = StartHour
            )
            StartTimes.append(date)

        # REMOVED CODE TO CHECK START TIMES TO MAKE SURE THERE IS A COMPLETE SET
        # AND GENERATE NEW TIME(S) IF NOT B/C IT WAS CODED TO BE SPECIFIC TO
        # COAST TRADER APPLICATION.  NEED TO ADD A MORE GENERAL SOLUTION.

        stats = {}
        try: # more than one season
            outfilename = os.path.join(RootDir, f"{season}Starts{NumStarts}.txt")
        except: # one season
            outfilename = os.path.join(RootDir, f"{season}Starts{NumStarts}.txt")
        outfile = open(outfilename, 'w')
        print("Writing:", outfilename)

        for time in StartTimes:
            stats[time.year] = stats.setdefault(time.year, 1) + 1
            outfile.write(time.strftime('%Y, %m, %d, %H, %M\n'))
        outfile.close()

def file_map(directories, reload = True):
    """
    Loads all netcdf files in the subdirectories of the parent model output
    directory and outputs:
       (1) a csv file with columns for a file index, the start time of the file,
           and the file path; and/or
       (2) a text file with paths to currupted files.
    The output location of files is the same as the parent directory.

    :param directories: dictionary with {"tag name":Path("/parent/directory/path"), ...}
    :type dictionary: {'string': pathlib.Path object, ...}
    
    """

    # create list of files to pass back
    paths_to_good_file_lists = []
    paths_to_bad_file_lists = []
    # Generate names for output files
    good_output={}
    lame_output={}
    for file_type in [*directories]:
        good_output[file_type] = directories[file_type]/f"{file_type}_TimeMap.csv"
        lame_output[file_type] = directories[file_type]/f"{file_type}_Grumpy.txt"
        paths_to_good_file_lists.append(good_output[file_type])
        paths_to_bad_file_lists.append(lame_output[file_type])

    # Reload existing output files or create new
    if reload:
        print('*** reloading time map ***')
        return paths_to_good_file_lists, paths_to_bad_file_lists
    else:
        print('*** generating time map ***')

        for file_type in [*directories]:

            print(f'*** {file_type} ***')

            # Initialize list of lame files that don't play well with xarray
            lame_files = []

            # create a file map for each file type
            file_map = {}
            file_map['start_datetime'] = []
            file_map['file_path'] = []

            # create list of netcdf files
            netcdf_file_list=[]

            for root, dirs, files in os.walk(directories[file_type]):
                sub_dir_list = [
                    os.path.join(root, file) for file in files if file.endswith(".nc")
                ]
                if sub_dir_list:
                    netcdf_file_list.extend(sub_dir_list)

            # loop through list to get start time and file path
            for netcdf_file in netcdf_file_list:
                with xr.open_dataset(netcdf_file) as ds:
                    skip = False
                    print(f'loaded: {netcdf_file}')
                    for var in [*ds]:
                        if not skip:
                            if (len(ds[var].shape) == 3) or (len(ds[var].shape) == 4):
                                # get name of time variable from 3D or 4D variable
                                time_variable = gridded.time.Time.locate_time_var_from_var(ds[var])
                                # get time stamp of first saved output timestep
                                if time_variable is not None:
                                    try: # make sure values exist at all time steps
                                        test = ds.variables[var][:]
                                    except:
                                        lame_files.append(netcdf_file)
                                        print(f'lame_file [{var}]: {netcdf_file}')
                                        #break
                                    if ds[time_variable].size > 0:
                                        try:
                                            file_start_time = ds[time_variable][0].values.astype(
                                                'datetime64[s]'
                                            ).tolist()
                                            file_map['file_path'].append(netcdf_file)
                                            file_map['start_datetime'].append(
                                                file_start_time.strftime('%Y-%m-%dT%H:%M')
                                            )
                                            skip = True
                                            print('SUCCESS! ',
                                                  file_start_time.strftime('%Y-%m-%dT%H:%M'),
                                                  ", ", netcdf_file
                                                 )
                                        except NameError:
                                            print(f"This netcdf file is missing a variable with time: {netcdf_file}")
                                            lame_files.append(netcdf_file)
                                            #raise
                                    else:
                                        print(f"Empty file.  Go fish! ")
                                        lame_files.append(netcdf_file)


                #ds.close()

            #######
            # create a dataframe and save to time_map excel
            output_csv = directories[file_type]/f"{file_type}_TimeMap.csv"
            print(f"Writing: {output_csv}")
            df = pd.DataFrame(file_map)
            df = df.sort_values('start_datetime')
            df.index.name = "index"
            # Reset the index so it's in order to start_datetime order
            # change "drop=False" if keeping original index number
            # as a new column is desired
            df.reset_index(drop=True, inplace=True)

            df.to_csv(output_csv)


            # create text file with a list of files that aren't included in time map
            if lame_files:
                lame_output = directories[file_type]/f"{file_type}_Grumpy.txt"
                print(f"Writing: {lame_output}")
                with open(lame_output, 'w') as f:
                    for files in lame_files:
                        f.write("%s\n" % files)



