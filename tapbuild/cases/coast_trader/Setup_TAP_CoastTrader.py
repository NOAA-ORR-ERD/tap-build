"""
TAP Setup.py

Master set up script for a TAP run

All the data required to set up and build TAP cubes + site.txt file should be in here

"""

import os
from datetime import datetime
import numpy as np
import time

# start timer
start_time = time.time()

# Location to read and write files for this TAP application
# RootDir = "/data/dylan/TapSites/SouthernCalifornia"    
RootDir = "/Users/rachael.mueller/Projects/SpillScenarioFiles/2024/CoastTrader"
OutputDir = "/Users/rachael.mueller/Projects/SpillScenarioFiles/2024/CoastTrader/TAP_test"
# upwelling case zuvts_his_Rachael_Exp42d_NNNN.nc with NNNN from 2801-2862


density = 0.99 #g/cm3 (https://adios.orr.noaa.gov/oils/EC00540)
total_tonnes = 492

# ~~~~~~~~  CURRENTS ~~~~~~~~~
Data_DirC = RootDir + "/model_input/WCOFS_current/up_down_welling/" 
current_files = []
for ftmp in  os.listdir(Data_DirC):
    if ftmp[-3:] == '.nc':
        current_files.append(os.path.join(Data_DirC, ftmp))
current_files.sort()
#print(f"Current files: {current_files, Data_DirC}")
# ~~~~~~~~~  WINDS ~~~~~~~~~
#only one wind file
wind_files = [
    RootDir + "/model_input/ERA5_wind/wind_wcofs_EraGrid_ref20080101_2016_rdm.nc"
]

# ~~~~~~~~~~~ MAP ~~~~~~~~~~
# Inputs needed for PyGnome
MapFileName = RootDir + "/model_input/coast_trader.bna"
MapFileType = "BNA"

# ~~~~~~~~~~~ OIL ~~~~~~~~~~
oil_file = RootDir + "/model_input/oil_types/bunker-c-1987_EC00539.json"
#oil_file = RootDir + "/model_input/oil_types/light-louisianna-sweet-bp_AD01554.json"

# ~~~~~~ TAP SELECTIONS ~~~~~
BuildStartTimes = True
RunPyGnome = True
BuildCubes = True
BuildSite = True
BuildViewer = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`
# Number of runs
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`
NumStarts = int(100) # number of start times you want in each season:


###################################
###### **** User Inputs **** ######
###################################

# Spill information
StartSites = [[ '-125.691, 48.27','AD02052','Coast Trader Location'],]

VariableMass = True #True  # True if you want GNOME runs with weathering 
                     # (must have ADIOS oil json files available )
waterTemp = 290
waterSal = 33
SpillAmount = [1000, 'bbl']
NumLEs = 1000 # number of Lagrangian elements you want in the GNOME run
ReleaseLength = 0 # Length of release in hours (0 for instantaneous)


# these are the days used to create the data cube
days = [1, 2, 3, 5, 7]

refloat = -1
windage_range = (0.01,0.03)
windage_persist = 900
diffusion_coef = 10000  # 1.e4
model_timestep = 15*60 # timestep in seconds

TimeSeries = None
# use None for no post-processing weathering -- weathering can be post-processed by the TAP
# viewer for instantaneous releases (see OilWeathering.py)
OilWeatheringType = None

##############################################################
###### Additional Calculations (and less common inputs) ######
##############################################################
Project = os.path.basename(OutputDir)

OutputTimes = [24*i for i in days] # output times in hours 
OutputUserStrings = ['%d days'%i for i in days]
OutputTimestep = 4 #hours
TrajectoryRunLength = 24 * max(days)
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
class Grid:
	pass

Grid.min_lat = 46.2583 # Astoria-ish # decimal degrees
Grid.max_lat = 49.75 
Grid.min_long = -127.338
Grid.max_long = -124.001
N_km = 2.5  # ~2 km is ~55 cells per degree north
Ncells_lat = 110 * (Grid.max_lat - Grid.min_lat) / N_km
Grid.dlat = (Grid.max_lat - Grid.min_lat)/Ncells_lat 
# 2570/N_km #2570 from Google Earth.  Eventually update with function. 
Ncells_lon = 100 
# 2.33km at 30N, 2.25km at 36N
Grid.dlong = (Grid.max_long - Grid.min_long)/Ncells_lon       

Grid.num_lat = int(
    np.ceil(np.abs(Grid.max_lat - Grid.min_lat)/Grid.dlat) + 1
)
Grid.num_long = int(
    np.ceil(np.abs(Grid.max_long - Grid.min_long)/Grid.dlong) + 1
)


PresetLOCS = ['5 barrels', '10 barrels', '20 barrels']
PresetSpillAmounts = ['1000 barrels', '100 barrels']


## TAP Viewer Data (for SITE.TXT file), where the TAP view, etc lives.
TAPViewerSource = os.path.join(os.path.dirname(RootDir),'TapFiles') 
## setup for the Viewer"
TAPViewerPath = Project + "_TapView" 
# TAPViewerPath = Project + "_TapView_" + str(NumLEs)

#########################################################################
# Loop through seasons and run scripts for each season
#########################################################################

# "upwelling case completed 199 runs before throwing an error
# Adding this to keep setup but skip to downwelling
# if case == "upwelling":
#     continue

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Build start times
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# time span of your data set
# DataStartEnd = (datetime(2004, 1, 1, 1), datetime(2004, 2, 26, 23))

# specification for how you want seasons to be defined, as a list of lists:
#  [name, (months) ]
#    name is a string for the season name  
#    months is a tuple of integers indicating which months are in that season
Seasons = [
   ['Upwelling',  [6]],
   ['Downwelling',  [1]]
]

StartTimeFiles = [
    (os.path.join(OutputDir, s[0]+'Starts.txt'), s[0]) 
    for s in Seasons
]

for Season in StartTimeFiles:
    print(Season)
    
DataGaps = ( )
print(f"---Run length = {TrajectoryRunLength} hours---")       
if BuildStartTimes and __name__ == '__main__':
    from tapbuild import BuildStartTimes
    for season in Seasons:
        print(f"---Building Start Times for {season[0]}---") 
        if season[0]=="Upwelling":
            DataStartEnd = (
                datetime(2016, 6, 1, 1), 
                datetime(2016, 6, 30, 23)
            )
        else:
            DataStartEnd = (
                datetime(2016, 1, 1, 1), 
                datetime(2016, 1, 31, 23)
            )
        BuildStartTimes.main(
            OutputDir, DataStartEnd, DataGaps, 
            season, NumStarts, TrajectoryRunLength, 
            TimeSeries
        )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run PyGNOME
end_time = time.time()
elapsed = (end_time - start_time)/3600
print(f'Time up to running PyGNOME: {elapsed} hrs')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if RunPyGnome and __name__ == '__main__':
    print("\n---Running PyGnome---")
    from tapbuild.cases.coast_trader import RunPyGnome_CoastTrader as RunPyGnome
    RunPyGnome.main(
        OutputDir, StartSites, RunSites, NumStarts, RunStarts,
        ReleaseLength, TrajectoryRunLength, StartTimeFiles, 
        TrajectoriesPath, NumLEs, MapFileName, refloat, 
        current_files, wind_files, oil_file, diffusion_coef,
        model_timestep, windage_range, windage_persist, 
        OutputTimestep, VariableMass,waterTemp,waterSal,
        SpillAmount
    )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Build Cubes
end_time = time.time()
elapsed = (end_time - start_time)/3600
print(f'Time up to building Cubes: {elapsed} hrs')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Cube root names are built to match the start time files
CubesRootNames = ['coast_trader' for i in StartTimeFiles] 

if BuildCubes and __name__ == '__main__':
    print("\n---Building Cubes---")
    from tapbuild import BuildCubes
    BuildCubes.main(
        OutputDir, CubesPath, CubesRootNames, CubeType, 
        CubeDataType, Seasons, TrajectoriesPath, ReceptorType, 
        Grid, OilWeatheringType, OutputTimes, NumLEs, VariableMass)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Build Site
end_time = time.time()
elapsed = (end_time - start_time)/3600
print(f'Time up to building Site: {elapsed} hrs')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if BuildSite and __name__ == '__main__':
    print("\n---Building Sites---")
    from tapbuild import BuildSite
    BuildSite.main(
        OutputDir, MapName, MapFileName, MapFileType, NumStarts, 
        Seasons, StartSites, OutputTimes, OutputUserStrings, 
        PresetLOCS, PresetSpillAmounts, ReceptorType, Grid,
        CubesRootNames
    )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Build Viewer
end_time = time.time()
elapsed = (end_time - start_time)/3600
print(f'Time up to building Viewer: {elapsed} hrs')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if BuildViewer and __name__ == '__main__':
    print("\n---Building Viewer---")
    from tapbuild import BuildViewer
    BuildViewer.main(
        OutputDir, TAPViewerPath, TAPViewerSource, MapFileName, 
        CubesPath, Seasons
    )

end_time = time.time()

elapsed = (end_time - start_time)/3600

print(f'Total time: {elapsed} hrs')
