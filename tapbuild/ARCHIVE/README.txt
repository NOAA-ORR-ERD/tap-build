

A library of scripts, etc. for buiding a  "TAP" location with py_gnome.

This is still in the protype stage and could use a significant refactoring. 

An example call for any of the scripts looks like this. 
	python BuildStartTimes.py SiteRootDir [RunLimStart RunLimEnd] [SiteStart SiteEnd]

The RunLim and Sites variables are optional and were a quick fix to wanting to be able to run subsets of the pygnome runs on a multi-processor machine. 


-  Setup_TAP.py - Where all the parameters/directories/filenames are defined for each of the scripts. 

-  BuildStartTimes.py - Takes the time range of the forcing files and picks the asked for number of random start times within that range. 

-  RunPyGnome.py - The heavy lifting script. Runs pygnome at the asked for start sites and start times. Writes the netcdf trajectory files to a trajectories sub-folder. 

-  BuildCubes.py - Builds the TAP data cubes from the computed trajectory files. 

-  BuildSite.txt.py* - Produces a site.txt file for the TAP run. site.txt is used by the TAP viewer to define needed input.

-  BuildViewer.py* - simple script that moves all the needed files to a viewer directory. 

-  TapFiles/ - Sub-dir with the structure and needed files for the TAP viewer

-  README.txt - this file. 

-  TAP_Setup.py* - loads the Setup-TAP patameters

-  tapbuild.py - skeleton file for future script development

