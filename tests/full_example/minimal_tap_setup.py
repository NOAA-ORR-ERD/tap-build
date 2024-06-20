"""
Minimal setup file for tapbuild.

Only what's needed for the tests.

"""

import os
from datetime import datetime
from pathlib import Path
import numpy as np

# whether the model should be re-initialized each time its run.
# if False, it will be initialized once, and only variable
# parameters are changed for each run
re_initialize_model = True

# Location to read and write files for this TAP application
# this example is relative to the location of this setup script
#  -- but you can hard-code anything.
RootDir = Path(__file__).parent

RootDir.mkdir(parents=True, exist_ok=True)

pygnome_script = RootDir / "make_gnome_model.py"
    
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

ReleaseLength = 1 # Length of release in hours (0 for instantaneous)

# time span of your data set
DataStartEnd = (datetime(2004, 1, 1, 1), datetime(2013, 12, 31, 23))
DataGaps = None

# specification for how you want seasons to be defined, as a list of lists:
#  [name, (months) ]
#    name is a string for the season name  
#    months is a tuple of integers indicating which months are in that season
Seasons = [
           ['Summer', [6,7,8,9,10,11]],
           ['Winter', [12,1,2,3,4,5]]
           ]

NumStarts = 2 # number of start times you want in each season:


##############################################################
###### Additional Calculations (and less common inputs) ######
##############################################################
Project = "Test Example"

StartTimeFiles = [(os.path.join(RootDir, s[0]+'Starts.txt'), s[0]) for s in Seasons]

OutputTimes = [3, 6, 12, 24] # output times in hours
OutputUserStrings = [f"{i} hours" for i in OutputTimes]

OutputTimestep = 12  # hours
TrajectoryRunLength = max(OutputTimes)
TrajectoriesPath = RootDir / 'TrajectoriesOut'  # relative to RootDir
MapName = Project + ' TAP'
CubesPath = 'Cubes'
CubesRootNames = ['MIN_' for i in StartTimeFiles] # built to match the start time files

VariableMass = True  # True if you want GNOME runs with weathering
                     # (must have ADIOS oil json files available )

SpillAmount = (1000, 'bbl')
NumLEs = 1000 # number of Lagrangian elements you want in the GNOME run


## Cube Builder Data
ReceptorType = 'Grid' # should be either "Grid" or "Polygons" (only grid is supported at the moment)
CubeType = 'Volume' # should be either "Volume" or "Cumulative"
CubeDataType = 'float32'

TimeSeries = None

# If ReceptorType is Grid, you need these, it defines the GRID
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
