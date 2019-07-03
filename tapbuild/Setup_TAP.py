"""
TAP Setup.py

Master set up script for a TAP run

All the data required to set up and build TAP cubes + site.txt file should be in here

"""

import os
from datetime import datetime
import numpy as np

# Location to read and write files for this TAP application
RootDir = "C:/Users/whit162/Documents/Projects/ARPA-E/GNOMEFiles/TAPbuild-master/tapbuild/Pacific_PrimarySimulation_Oct2018"
if not os.path.exists(RootDir):
    os.makedirs(RootDir)
    
# Location of Gnome data forcing
Data_Dir = "C:/Users/whit162/Documents/Projects/ARPA-E/GNOMEFiles"
if not os.path.exists(Data_Dir):
    raise Exception("RootDir: %s Doesn't exist"%Data_Dir)

BuildStartTimes = True
RunPyGnome = True
BuildCubes = True
BuildSite = True
BuildViewer = True

###################################
###### **** User Inputs **** ######
###################################
print "\nAnalyzing User Inputs"

# Spill information
#StartSites = ['-125.7, 48.2', '-125.15, 47.8', '-125.2, 48.2', '-125, 47.1']
StartSites = ['-125.74,48.04', '-126.19,47.83', '-126.64,47.62', '-127.09,47.41',
              '-127.54,47.20', '-127.99,46.99', '-128.44,46.78', '-125.23,47.66',
              '-125.68,47.45', '-126.13,47.24', '-126.58,47.03', '-127.03,46.82',
              '-127.48,46.61', '-127.93,46.40', '-128.38,46.19', '-125.13,47.07',
              '-125.58,46.86', '-126.03,46.65', '-126.48,46.44', '-126.93,46.23',
              '-127.38,46.02', '-127.83,45.81', '-128.28,45.60', '-124.45,46.85',
              '-124.90,46.64', '-125.35,46.43', '-125.80,46.22', '-126.25,46.01',
              '-125.70,43.70', '-127.00,43.70'] #30 start locations
OilType = None

NumLEs = 10000 # number of Lagrangian elements you want in the GNOME run
ReleaseLength = 7*24 # Length of release in hours (0 for instantaneous)

# time span of your data set
DataStartEnd = (datetime(2000, 1, 1, 1), datetime(2010, 12, 31, 23))
DataGaps = ( )

# specification for how you want seasons to be defined, as a list of lists:
#  [name, (months) ]
#    name is a string for the season name  
#    months is a tuple of integers indicating which months are in that season
Seasons = ['AllYear', [1,2,3,4,5,6,7,8,9,10,11,12]]
#Seasons = [
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
NumStarts = 200 # number of start times you want in each season:

days = [1, 2, 3, 4, 5, 7, 10, 14, 21]
# days = [1, 3, 5, 7, 10, 15, 20, 30, 50, 70, 90, 120, 135, 150]

# Inputs needed for PyGnome
MapFileName, MapFileType = ('coast_Pacific.bna', 'BNA')

current_files = [
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2000_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2001_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2002_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2003_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2004_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2005_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2006_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2007_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2008_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2009_Pacific.nc"),
                 os.path.join(Data_Dir,"HYCOM_3hrly_2Depth_2010_Pacific.nc")
                ]

wind_files = [
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2000_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2001_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2002_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2003_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2004_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2005_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2006_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2007_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2008_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2009_Pacific.nc"),
              os.path.join(Data_Dir,"CFSRWind_0.5deg_10m_2010_Pacific.nc")
             ]

refloat = -1
windage_range = (0.03,0.03)
windage_persist = -1
diffusion_coef = 5000
model_timestep = 30*60 # timestep in seconds

##############################################################
###### Additional Calculations (and less common inputs) ######
##############################################################
Project = os.path.basename(RootDir)
StartTimeFiles = [(os.path.join(RootDir, s[0]+'Starts.txt'), s[0]) for s in Seasons]
OutputTimes = [24*i for i in days] # output times in hours (calculated from days)
OutputUserStrings = ['%d days'%i for i in days]
OutputTimestep = 12 #hours
TrajectoryRunLength = 24 * max(days)
TrajectoriesPath = 'Trajectories_n' + str(NumLEs) # relative to RootDir
MapName = Project + ' TAP'
CubesPath = 'Cubes_n' + str(NumLEs)
CubesRootNames = ['Arc_' for i in StartTimeFiles] # built to match the start time files

# Can be used to filter out some start sites and start times
# These variables function as an index map
s0,s1 = [0,len(StartSites)]
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
CubeDataType = 'uint8'

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
### I would like this grid resolution, but it throws an error in TAP ###
#Grid.dlat = 0.05       # ~68.88 miles per degree
#Grid.dlong = 0.05       # 60 mi per degree at 30N, 53 mi at 40N, 44.5 mi at 50N
Grid.min_lat = 30.0 # decimal degrees
Grid.max_lat = 50.0
Grid.dlat = 0.2       # ~68.88 miles per degree
Grid.min_long = -130.0
Grid.max_long = -115.0
Grid.dlong = 0.2       # 60 mi per degree at 30N, 53 mi at 40N, 44.5 mi at 50N

Grid.num_lat = int(np.ceil(np.abs(Grid.max_lat - Grid.min_lat)/Grid.dlat) + 1)
Grid.num_long = int(np.ceil(np.abs(Grid.max_long - Grid.min_long)/Grid.dlong) + 1)

# use None for no weathering -- weathering can be post-processed by the TAP
# viewer for instantaneous releases (see OilWeathering.py)
OilWeatheringType = None
PresetLOCS = ['5 barrels', '10 barrels', '20 barrels']
PresetSpillAmounts = ['1000 barrels', '100 barrels']

## TAP Viewer Data (for SITE.TXT file)
TAPViewerSource = os.path.join(os.path.dirname(RootDir),'TapFiles') # where the TAP view, etc lives.
## setup for the Viewer"
TAPViewerPath = Project + "_TapView_" + str(NumLEs)

#############################
###### Running Scripts ######
#############################
if BuildStartTimes and __name__ == '__main__':
    print "\n---Building Start Times---"
    import BuildStartTimes
    BuildStartTimes.main(RootDir, DataStartEnd, DataGaps, Seasons, NumStarts, TrajectoryRunLength, TimeSeries)

if RunPyGnome and __name__ == '__main__':
    print "\n---Running PyGnome---"
    import RunPyGnome
    RunPyGnome.main(RootDir, Data_Dir, StartSites, RunSites, NumStarts, RunStarts,
                    ReleaseLength, TrajectoryRunLength,
                    StartTimeFiles,  TrajectoriesPath, 
                    NumLEs, MapFileName, refloat, current_files, wind_files, diffusion_coef,
                    model_timestep, windage_range, windage_persist, OutputTimestep)

if BuildCubes and __name__ == '__main__':
    print "\n---Building Cubes---"
    import BuildCubes
    BuildCubes.main(RootDir, CubesPath, CubesRootNames, CubeType, CubeDataType, Seasons,
                    TrajectoriesPath, ReceptorType, Grid, OilWeatheringType, OutputTimes, NumLEs, VariableMass)

if BuildSite and __name__ == '__main__':
    print "\n---Building Sites---"
    import BuildSite
    BuildSite.main(RootDir, MapName, MapFileName, MapFileType, NumStarts, Seasons,
                   StartSites, OutputTimes, OutputUserStrings, PresetLOCS,
                   PresetSpillAmounts, ReceptorType, Grid)

if BuildViewer and __name__ == '__main__':
    print "\n---Building Viewer---"
    import BuildViewer
    BuildViewer.main(RootDir, TAPViewerPath, TAPViewerSource, MapFileName, CubesPath, Seasons)
