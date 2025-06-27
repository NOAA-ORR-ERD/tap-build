#!/usr/bin/env python
"""
Code to build the setup for the Tap Viewer

Currently, it builds an old-style site.txt file, that can be converted to a site.json file

Ultimately, it can be updated to directly build a site.json file(s)
"""

import os

from .utilities import load_config
from . import tap_mod

print(tap_mod)

def build_site(config_file):

    config = load_config(config_file)

# def main(RootDir, MapName, MapFileName, MapFileType, NumStarts, Seasons, StartSites,
#          OutputTimes, OutputUserStrings, PresetLOCS, PresetSpillAmounts, ReceptorType,
#          Grid,CubesRootNames):
    # unpacking this all from config for compatibility with old code,
    # and so that it's explicit, ans we could change the names in config or
    # here.
    Seasons = config.Seasons
    RootDir = config.RootDir
    MapName = config.MapName
    MapFileName = config.MapFileName
    NumStarts = config.NumStarts
    CubesRootNames = config.CubesRootNames
    OutputTimes = config.OutputTimes
    OutputUserStrings = config.OutputUserStrings
    PresetSpillAmounts = config.PresetSpillAmounts
    PresetLOCS = config.PresetLOCS
    ReceptorType = config.ReceptorType
    StartSites = config.StartSites

    ## Fixme: we should consolidate this somehow
    Receptors = tap_mod.Grid(**config.Grid)

    print("starting")
    
    StartTimeFiles = [(os.path.join(RootDir, s[0]+'Starts.txt'), s[0]) for s in Seasons]
    # CubesRootNames = ["Arc_" for i in StartTimeFiles] # built to match the start time files
    

    file = open(os.path.join(RootDir,"site.txt"),'w')
    
    file.write('"%s"  //Map Name for User\n'%MapName)
    file.write('"%s"  "%s"  // "map file name"  "map file type" -- either "BNA"  \n'%(MapFileName, "BNA") )
    file.write('%i SPILLS // number of spills per site and time in every cube  \n'%NumStarts )
    file.write('%i SEASONS\n'%len(Seasons) )
    for i in range(len(Seasons)):
        Season = Seasons[i][0]
        file.write('"%s" "%s" "%s" // Name for menu, prefix of cube names, name of directory\n'%
                   (Season, CubesRootNames[i], Season) )
    file.write('%i TIMES \n'%(len(OutputTimes)) )
    #reverse output times:
    OutputTimes.reverse()
    OutputUserStrings.reverse()
    for OutputTime, OutputUserString in zip(OutputTimes, OutputUserStrings):
        file.write('%i "%s" // numHours  "user string" blank user string means not in menu \n'%(
                   OutputTime, OutputUserString) )
    file.write('%i AMOUNTS // amounts of oil preset for the user\n'%len(PresetSpillAmounts) )
    for s in PresetSpillAmounts:
        file.write('%s  \n'%s )
                   
    file.write('%i LOCS // levels of concern (LOC) preset for the user \n'%len(PresetLOCS) )
    for s in PresetLOCS:
        file.write('%s  \n'%s )
    
    # now write the BNA of the receptor sites:
    if ReceptorType == "Grid":
        #file.write("This is where the receptors go\n")
        # from batch_gnome import tap_mod
        # Receptors = tap_mod.Grid(Grid.min_long, Grid.max_long, Grid.min_lat, Grid.max_lat,Grid.num_lat,Grid.num_long)
        file.write("%i SITES // number of sites\n"%Receptors.num_cells)
        Receptors.WriteBNA(file)
    else:
        raise ValueError("Only Grid receptor type is supported. You have: {ReceptorType}")
    
    # write cube locations:
    file.write("%i CUBES\n"%len(StartSites))

    print("Writing the start sites")
    for site in StartSites:
        lon, lat = site['start_position']
        file.write(f"{lon:.6f}, {lat:.6f}\n")

    file.close()
