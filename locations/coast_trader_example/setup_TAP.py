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

# If True: Model is initialized (What constitutes "initialize"?)
# If False, it will be initialized once, and only variable
# parameters are changed for each run
re_initialize_model = True

# RDM's interpretation of what initialization means
if re_initialize_model:
    reload_file_map = False
else:
    # Boolean flag for reload (True) or create (False) 
    # time-map files
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

#~~~~~~~~~~~~~~ RDM: I am here ~~~~~~~~~~~~~~~~~~
# Location of Gnome data forcing
# Data_DirC = "/data/dylan/SoCalTAP/Data/gnome_ucla/surface/"     # Gonzo
# Data_DirW = "/data/dylan/SoCalTAP/Data/gnome_ucla/wind/"

DataDir = RootDir / "data"

if not DataDir.is_dir:
    raise ValueError(f"DataDir: {DataDir} Doesn't exist")


###################################
###### **** User Inputs **** ######
###################################

# Spill information
# each start site has coords, name, and any other info needed by the GNOME run
StartSites = [{'start_position':(-117.211873, 32.682502),
               'name': 'Ellen',
               'oil_file': 'AD01438.json',
               'spill_amount': (1000, 'bbl'),
               },
              {'start_position':(-117.226992, 32.676416),
               'name': 'Elly',
               'oil_file': 'AD01438.json',
               'spill_amount': (1000, 'bbl'),
               },
              ]

# Refactor: move this kind of info into the PyGNOME config?

# OilType = None
VariableMass = True  # True if you want GNOME runs with weathering
                     # (must have ADIOS oil json files available )

# waterTemp = 290
# waterSal = 33
# # SpillAmount = [1, 'kg']

SpillAmount = (1000, 'bbl')


NumLEs = 1000 # number of Lagrangian elements you want in the GNOME run

ReleaseLength = 12 # Length of release in hours (0 for instantaneous)

# time span of your data set
# DataStartEnd = (datetime(2004, 1, 1, 1), datetime(2004, 2, 26, 23))
DataStartEnd = (datetime(2004, 1, 1, 1), datetime(2013, 12, 31, 23))
# still needed??
DataGaps = []

# specification for how you want seasons to be defined, as a list of lists:
#  [name, (months) ]
#    name is a string for the season name  
#    months is a tuple of integers indicating which months are in that season
Seasons = [
           ['Summer', [6,7,8,9,10,11]],
           ['Winter', [12,1,2,3,4,5]]
           ]
# Seasons = [
#            ['Spring',  [3, 4, 5 ]],
#            ['Summer',  [6, 7, 8 ]],
#            ['Fall',  [9, 10, 11]],
#          ]
# Seasons = [
#             ['Dec', [12]],
#             ['Jan', [1]],
#             ['Feb', [2]],
#             ['Mar', [3]],
#             ['Apr', [4]],
#             ['May', [5]],
#           ]

NumStarts = 10 # number of start times you want in each season:


# this is used to then compute the "real" variables:
output_times_in_days = [1, 2, 3, 5, 7]


##############################################################
###### Additional Calculations (and less common inputs) ######
##############################################################
Project = "Example"

StartTimeFiles = [(os.path.join(RootDir, s[0]+'Starts.txt'), s[0]) for s in Seasons]

output_times_in_days = [1, 2, 3, 5, 7] # temp for use to compute the below
OutputTimes = [24*i for i in output_times_in_days] # output times in hours (calculated from days)
OutputUserStrings = ['%d output_times_in_days'%i for i in output_times_in_days]
del output_times_in_days # not really required to delete, but safer

OutputTimestep = 12 #hours
TrajectoryRunLength = max(OutputTimes)
TrajectoriesPath = RootDir / 'TrajectoriesOut'
MapName = Project + ' TAP'
CubesPath = 'Cubes'
CubesRootNames = [f'EXAMPLE_{i[1]}' for i in StartTimeFiles] # built to match the start time files

# Can be used to filter out some start sites and start times
# These variables function as an index map
s0,s1 = [0, len(StartSites)]
RunSites = range(s0,s1)

r0,r1 = [0,NumStarts]
RunStarts = range(r0,r1)

## Cube Builder Data
ReceptorType = 'Grid' # should be either "Grid" or "Polygons" (only grid is supported at the moment)
CubeType = 'Volume' # should be either "Volume" or "Cumulative"
## CubeDataType options are: 'float32', 'uint16', or 'uint8'
##   float32 gives better precision for lots of LEs
##   uint8 saves disk space -- and is OK for about 1000 LEs
##   uint16 is a mid-point -- probably good to 10,000 LEs or so
CubeDataType = 'float32'

# Files with time series records in them used by GNOME
# These are used to compute the possible time files. The format is:
# It is a list of one or more time files. each file is desribed with a tuple:
#  (file name, allowed_gap_length, type)
#    file_name is a string
#    allowed_gap_length is in hours. It indicates how long a gap in the time
#         series records you will allow GNOME to interpolate over.
#    type is a string describing the type of the time series file. Options
#         are: "Wind", "Hyd" for Wind or hydrology type files
# if set to None, model start and end times will be used
#TimeSeries = [("WindData.OSM", datetime.timedelta(hours = 6), "Wind" ),]
TimeSeries = None

#If ReceptorType is Grid, you need these, it defines the GRID
class Grid:
	pass
Grid.min_lat = 32.0 # decimal degrees
Grid.max_lat = 35.5
Grid.dlat = 0.02       #  makes 2.23km tall receptor cells at 33N
Grid.min_long = 238.5
Grid.max_long = 243.74
Grid.dlong = 0.025       # 2.33km at 30N, 2.25km at 36N

Grid.num_lat = int(np.ceil(np.abs(Grid.max_lat - Grid.min_lat)/Grid.dlat) + 1)
Grid.num_long = int(np.ceil(np.abs(Grid.max_long - Grid.min_long)/Grid.dlong) + 1)

# use None for no post-processing weathering -- weathering can be post-processed by the TAP
# viewer for instantaneous releases (see OilWeathering.py)
OilWeatheringType = None
PresetLOCS = ['5 barrels', '10 barrels', '20 barrels']
PresetSpillAmounts = ['1000 barrels', '100 barrels']


# Inputs needed for PyGnome -- this is probably going elsewhere
# MapFileName, MapFileType = (os.path.join(RootDir,'SoCalcoast_pos.bna'), 'BNA')

# current_files = []
# for ftmp in  os.listdir(Data_DirC):
#     if ftmp[-3:] == '.nc':
#         current_files.append(os.path.join(Data_DirC, ftmp))

# wind_files = []
# for ftmp in  os.listdir(Data_DirW):
#     if ftmp[-3:] == '.nc':
#         wind_files.append(os.path.join(Data_DirW, ftmp))


# current_files = [
#                  os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2000_Pacific.nc"),
#                  os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2001_Pacific.nc"),
#                 ]

# wind_files = [
#               os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2000_Pacific.nc"),
#               os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2001_Pacific.nc"),
#              ]

# refloat = -1
# windage_range = (0.02,0.04)
# windage_persist = 900
# diffusion_coef = 10000  # 1.e4
# model_timestep = 15*60 # timestep in seconds
