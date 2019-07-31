#!/usr/bin/env python

"""
A simple script that copies all the cubes and everything into the right places

This has not been well set up to work universally. It's only been tested on one setup

"""


import os, shutil

# from TAP_Setup import setup


def main(RootDir, TAPViewerPath, TAPViewerSource, MapFileName, CubesPath, Seasons):

    TAPViewerDir = os.path.join(RootDir, TAPViewerPath)

    #Check if TAP Viewer Dir exists:
    if not os.path.isdir(TAPViewerDir):
        print "making new TAP Viewer Directory"
        os.mkdir(TAPViewerDir)

    # copy the exe and settings files
    shutil.copy(os.path.join(TAPViewerSource,'TAP.exe'), TAPViewerDir)
    shutil.copy(os.path.join(TAPViewerSource,'SETTINGS.TAP'), TAPViewerDir)

    # Check for TAPDATA
    TAPDATADir = os.path.join(TAPViewerDir,"TAPDATA")
    if not os.path.isdir(TAPDATADir):
        print "Making TAPDATA Directory"
        os.mkdir(TAPDATADir)

    # copy the TAPCONFIG file
    shutil.copy(os.path.join(TAPViewerSource, "TAPDATA", "TAPCONFIG.txt"), TAPDATADir)

    # copy the site.txt file
    shutil.copy(os.path.join(RootDir,"site.txt"), TAPDATADir)
    shutil.copy(os.path.join(TAPViewerSource, MapFileName), TAPDATADir)

    # copy the start times file (not required, but it's good to have it there
    # print StartTimeFiles
    # for (filename, _) in StartTimeFiles:
    #     shutil.copy(filename, TAPDATADir)

    FullCubesPath = os.path.join(RootDir, CubesPath) 

    for (season, junk) in Seasons:
        SeasonPath = os.path.join(TAPDATADir,season)
        if not os.path.isdir(SeasonPath):
            print "Creating:", SeasonPath
            os.mkdir(SeasonPath)
        SeasonCubesPath = os.path.join(FullCubesPath,season)
        print SeasonPath, SeasonCubesPath
        
        for name in os.listdir(SeasonCubesPath):
            print "Moving:", name
            shutil.move(os.path.join(SeasonCubesPath,name),
                         os.path.join(SeasonPath,name) )

    # These steps are both useful for archiving your TAP project, but not needed for
    # the TAP viewer to work. 

    # copy the script and Setup_TAP files to viewer dir for archive
    # setfile = os.path.join(RootDir,'Setup_TAP.py')
    # shutil.copy(setfile, TAPViewerDir)


    # move Trajectories to TapViewer dir
    # shutil.move(setup.TrajectoriesPath, TAPViewerDir)
 
    # copy the start times file (not required, but it's good to have it there
    # print StartTimeFiles
    # for (filename, _) in StartTimeFiles:
    #     shutil.copy(filename, TAPDATADir)


if __name__ == '__main__':
    import Setup_TAP as tap
    main(tap.RootDir, tap.CubesPath, tap.CubesRootNames, tap.CubeType, tap.CubeDataType,
         tap.Seasons, tap.TrajectoriesPath, tap.ReceptorType, tap.Grid, tap.OilWeatheringType,
         tap.OutputTimes, tap.NumLEs)
