"""
An adaptation of Chris' setup script to incorporate Coast Trader changes

Purpose: Uses `yaml` file inputs to setup TAP, run PyGNOME, and build TAP cubes

Requirements:
 - gnome_tap (or similar) environment
 - `ulimit` set to 10000 files.  Before running script, type into command line;
    % ulimit -n 10000 
 - yaml file created by `create_TAP_setup.ipynb` or setup equivalently
 
Environment: `gnome_tap`
    $ cd full_path_to/tapbuild/tapbuild
    $ conda env create -n gnome_tap --file requirements_tap.yaml
    $ conda activate gnome_tap

NOTE: it relies on a run_pygnome script that needs to be developed

"""

import os
import sys
import yaml
from datetime import datetime, timedelta
import calendar
import time # to track computation speed for this setup file
from pathlib import Path
import numpy as np
import pandas as pd
from glob import glob
import math # for build_grid class


from tapbuild.utilities import BuildGrid, WriteStartTimes, file_map

# start timer of computation speed
start_time = time.time()

###############################################################
# ****  NECCESSARY INPUTS IF THIS WERE A FUNCTION  **** ######
###############################################################

# setup yaml file
input_dir = Path(
    "/Users/tap.fn/Fury4/tap.fn/rachael/coast_trader/DFO_NOAA_90"
    #"/Users/rachael.mueller/Projects/SpillScenarioFiles/2024/CoastTrader/TAP"
)
setup_file = input_dir/"config.yaml"
# setup_file = 'make_gnome_model.py' # originally called "pygnome_script" but never used in this file

# desired naming convention for currents and winds
current_key = "ocean_currents"
wind_key = "winds"

# If True: Model will be initialized (What constitutes "initialize"?)
# If False, initialized files are loaded 
initialize_model = True

# RDM's interpretation of what initialization means
if initialize_model:
    # Create time-map files 
    reload_file_map = False
else:
    # Reload filemap that was already created
    reload_file_map = True

###############################################################
# Load .yaml and define variables
###############################################################

# load setup yaml file
with open(setup_file) as file:
    setup = yaml.load(file, Loader=yaml.Loader)

# Location to read and write files for this TAP application   
RootDir = Path(setup['directories']['root'])
OutputDir = Path(setup['directories']['outputs'])
# make directories if needed
RootDir.mkdir(parents=True, exist_ok=True)
OutputDir.mkdir(parents=True, exist_ok=True)
# # make output directory if it doesn't exist
# if not os.path.isdir(OutputDir):
#     os.mkdir(OutputDir)

###################################
###### **** FILES **** ######
###################################
# ~~~~~~~ NETCDF input files ~~~~
# dictionaries with paths to useable files and start times of files
# with identical key names to those in "directories"
file_paths={}
file_times={}

directories = {
    current_key : Path(setup['directories']['input_currents']),
    wind_key : Path(setup['directories']['input_winds'])
}

# pass back:
#  1) a list of .csv files with dates and paths for files in a given directory (e.g. for winds and currents)
#  2) a list of .csv files with dates and paths for files that are curropt or missing
# List lenth is same as directories dictionary length (in this case, 2)
# If the .csv files were created then their paths are passed back
# If "reload_file_map = False" then the .csv files are first created and then passed back
good_files_path, bad_files_path = xarray_file_map(  
    directories, 
    reload_file_map
)

# Loop through .csv files in "good_file_path".  
# Dictionary keys are same as "directory" keys if .csv's were created 
# through this script, but I assign "key_name" from the file name in case 
# the files are created separately.  Headers for .csv files need to be
# "file_path" and "start_datetime"
# This creates a dictionary for file paths and a dictionary for file_times,
# both with same indexing. 
for path in good_files_path:
    print(f"Loading: {path}")
    try: 
        df = pd.read_csv(path)
        key_name = "_".join(
            [str(item) 
             for item in str(path).split("/")[-1].split("_")[0:-1]
            ]
        )
        print(key_name)
        file_paths[key_name] = df['file_path']
        file_times[key_name] = df['start_datetime']
    except OSError:
       raise RuntimeError('File not found') from None

# ~~~ The next four lines of code seem unnecessary and worth getting rid of ~~~
# lists of file paths to current or wind forcing files
current_files = file_paths[current_key]
wind_files = file_paths[wind_key]
# list of start times for above files
current_time_map = file_times[current_key]
wind_time_map =  file_times[wind_key]

# ~~~~~~~~~~~ MAP ~~~~~~~~~~
# Inputs needed for PyGnome
MapFileName = setup['files']['map']
MapFileType = MapFileName[-3:]

# ~~~~~~~~~~~ OIL ~~~~~~~~~~
oil_file = setup['files']['oil']

# ~~~~~~~~~~~ GRID ~~~~~~~~~~
# needed for NEMO current files
grid_file = setup['files']['grid_file']

###################################
###### **** PARAMETERS **** ######
###################################

# ~~~~~~ SPILL INFORMATION ~~~~~
SpillAmount = setup['params']['spill_amount'] 
NumLEs = setup['params']['number_elements'] 
ReleaseLength = setup['params']['spill_duration'] 
refloat = setup['params']['refloat']
model_timestep = setup['params']['timestep']

# ~~~~~~ WEATHERING ~~~~~
VariableMass = setup['params']['variable_mass'] 
density = setup['params']['density']

# ~~~~~~ HYDROGRAPHY ~~~~~
waterTemp = setup['params']['water_temp']
waterSal = setup['params']['water_salinity']

# ~~~~~~ WINDS AND MOVERS ~~~~~
windage_range = setup['params']['windage_range']
windage_persist = setup['params']['windage_persist']
diffusion_coef = setup['params']['diffusion_coef'] 

# ~~~~~~ SPILL SPECIFICATIONS ~~~~~
StartSites = setup['params']['spill_sites']

# !!!!!! Change the StartSites to a dictionary, as shown below !!!!!!
# !!!!!! Add "NumLEs" so num particles can vary with spill_amount !!!!!!
# # Spill information
# # each start site has coords, name, and any other info needed by the GNOME run
# StartSites = [{'start_position':(-117.211873, 32.682502),
#                'name': 'Ellen',
#                'oil_file': 'AD01438.json',
#                'spill_amount': (1000, 'bbl'),
#                },
#               {'start_position':(-117.226992, 32.676416),
#                'name': 'Elly',
#                'oil_file': 'AD01438.json',
#                'spill_amount': (1000, 'bbl'),
#                },
#               ]


# ~~~~~~ TAP SELECTIONS ~~~~~
NumStarts = int(setup['tap']['num_spills']) 
days = setup['tap']['cube_days']
Seasons = setup['tap']['seasons']
StartTimeFiles = [(os.path.join(RootDir, s[0]+'Starts.txt'), s[0]) for s in Seasons]

# !!!!  convert seasons into a dictionary !!!!
# Seasons = [
#            ['Summer', [6,7,8,9,10,11]],
#            ['Winter', [12,1,2,3,4,5]]
#            ]

# ~~~~~~ CODE SELECTION ~~~~~
# true/false statements to turn on/off different code functions
BuildStartTimes = setup['tap_build']['BuildStartTimes']
RunPyGnome = setup['tap_build']['RunPyGnome']
BuildCubes = setup['tap_build']['BuildCubes']
BuildSite = setup['tap_build']['BuildSite']
#BuildViewer = setup['tap_build']['BuildViewer']

#~~~~~~~~~ Consider removing  ~~~~~~~~~~~~`
# viewer for instantaneous releases (see OilWeathering.py)
OilWeatheringType = None

##############################################################
###### Additional Calculations (and less common inputs) ######
##############################################################
Project = os.path.basename(OutputDir)

OutputTimes = [24*i for i in days] # output times in hours 
OutputUserStrings = ['%d days'%i for i in days]
# hours between writing output to file
OutputTimestep = setup['params']['OutputTimestep'] 
TrajectoryDuration = setup['params']['TrajectoryDuration']
TrajectoriesPath = 'TrajectoriesOut'  # relative to RootDir
MapName = Project + 'Coast Trader TAP'
CubesPath = 'Cubes'

# Can be used to filter out some start sites and start times
# These variables function as an index map
s0,s1 = [0,len(StartSites)]
RunSites = range(s0,s1)

r0,r1 = [0,NumStarts]
RunStarts = range(r0,r1)

## Cube Builder Data
ReceptorType = 'Grid' 
CubeType = 'Volume' # should be either "Volume" or "Cumulative"
## CubeDataType options are: 'float32', 'uint16', or 'uint8'
##   float32 gives better precision for lots of LEs
##   uint8 saves disk space -- and is OK for about 1000 LEs
##   uint16 is a mid-point -- probably good to 10,000 LEs or so
CubeDataType = 'float32'

Grid = BuildGrid(
    setup['tap']['min_lat'], 
    setup['tap']['max_lat'], 
    setup['tap']['min_lon'], 
    setup['tap']['max_lon'],
    setup['tap']['d_lat'],
    setup['tap']['d_lon']
)

# The following two are for TAP viewer 
PresetLOCS = setup['site']['levels_of_concern']
PresetSpillAmounts = setup['site']['spill_volumes'] # adjustable spill amounts in TAP viewer

## TAP Viewer Data (for SITE.TXT file), where the TAP view, etc lives.
TAPViewerSource = os.path.join(os.path.dirname(RootDir),'TapFiles') 
## setup for the Viewer"
TAPViewerPath = Project + "_TapView" 


##############################################################
###### Additional Calculations (and less common inputs) ######
##############################################################
#Project = "Example"

#StartTimeFiles = [(os.path.join(RootDir, s[0]+'Starts.txt'), s[0]) for s in Seasons]


