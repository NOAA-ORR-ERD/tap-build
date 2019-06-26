#!/usr/bin/env python

import os
from datetime import datetime, timedelta

from gnome.scripting import surface_point_line_spill
from gnome.outputters import NetCDFOutput

from gnome.model import Model
from gnome.utilities.remote_data import get_datafile
from gnome.map import MapFromBNA

from gnome.movers import PyWindMover, RandomMover, PyCurrentMover

import gc


def main(RootDir, Data_Dir, StartSites, RunSites, NumStarts, RunStarts, ReleaseLength,
         TrajectoryRunLength, StartTimeFiles, TrajectoriesPath, NumLEs, MapFileName,
         refloat, current_files, wind_files, diffusion_coef, model_timestep,
         windage_range, windage_persist, OutputTimestep):
    
    # timingRecord = open(os.path.join(RootDir,"timing.txt"),"w")
    # count = len(StartTimeFiles) * len(RunStarts) * len(RunSites)
    # timingRecord.write("This file tracks the time to process "+str(count)+" gnome runs")
    
    # model timing
    release_duration = timedelta(hours=ReleaseLength)
    run_time = timedelta(hours=TrajectoryRunLength)
    
    # initiate model
    model = Model(duration=run_time,
                  time_step=model_timestep,
                  uncertain=False)
    
    # determine boundary for model
    print "Adding the map:",MapFileName
    mapfile = get_datafile(os.path.join(Data_Dir, MapFileName))
    model.map = MapFromBNA(mapfile, refloat_halflife=refloat)
    
        
    # loop through seasons
    for Season in StartTimeFiles:
        # timer1 = datetime.now()
        
        SeasonName = Season[1]
        start_times = open(Season[0],'r').readlines()[:NumStarts]
        make_dir(os.path.join(RootDir,TrajectoriesPath,SeasonName))
        print "  Season:",SeasonName
        
        # get and parse start times in this season
        start_dt = []
        for start_time in start_times:
            start_time = [int(i) for i in start_time.split(',')]
            start_time = datetime(start_time[0],start_time[1],start_time[2],start_time[3],start_time[4])
            start_dt.append(start_time)
        
        ## loop through start times
        for time_idx in RunStarts:
            # timer2 = datetime.now()
            
            gc.collect()
            model.movers.clear()
            
            ## set the start location
            start_time = start_dt[time_idx]
            end_time = start_time + run_time
            model.start_time = start_time
            print "  ",start_time,"to",end_time
            
            ## get a list of the only data files needed for the start time (less data used)
            ## note: requires data files in year increments
            years = range(start_time.year, end_time.year + 1)
            years = [str(i) for i in years]
            wind = [s for s in wind_files if any(xs in s for xs in years)]
            current = [s for s in current_files if any(xs in s for xs in years)]
            
            ## add wind movers
            w_mover = PyWindMover(filename=wind)
            model.movers += w_mover
            
            ## add current movers
            c_mover = PyCurrentMover.from_netCDF(current)
            model.movers += c_mover
            
            ## add diffusion
            model.movers += RandomMover(diffusion_coef=diffusion_coef)
            
            ## loop through start locations
            for pos_idx in RunSites:
                # timer3 = datetime.now()
                
                start_position = [float(i) for i in StartSites[pos_idx].split(',')]
                
                OutDir = os.path.join(RootDir,TrajectoriesPath,SeasonName,'pos_%03i'%(pos_idx+1))
                make_dir(OutDir)
                
                print "    ",pos_idx,time_idx
                print "    Running: start time:",start_time,
                print "at start location:",start_position
                
                ## set the spill to the location
                spill = surface_point_line_spill(num_elements=NumLEs,
                                                 start_position=(start_position[0], start_position[1], 0.0),
                                                 release_time=start_time,
                                                 end_release_time=start_time+release_duration,
                                                 windage_range=windage_range,
                                                 windage_persist=windage_persist)
                
                # print "adding netcdf output"
                netcdf_output_file = os.path.join(OutDir,'pos_%03i-t%03i_%08i.nc'
                                                  %(pos_idx+1, time_idx,int(start_time.strftime('%y%m%d%H'))),
                                                  )
                model.outputters.clear()
                model.outputters += NetCDFOutput(netcdf_output_file,output_timestep=timedelta(hours=OutputTimestep))
                
                model.spills.clear()
                model.spills += spill
                
                model.full_run(rewind=True)
                
    #             timer4 = datetime.now()
    #             diff = round((timer4-timer3).total_seconds() / 60, 2)
    #             timingRecord.write("\t\t"+str(pos_idx)+" took "+str(diff)+" minutes to complete")
    #         diff = round((timer4-timer2).total_seconds() / 3600, 2)
    #         count = len(RunSites)
    #         timingRecord.write("\t"+str(time_idx)+" took "+str(diff)+" hours to finish "+str(count)+" Gnome runs")
    #     diff = round((timer4-timer1).total_seconds() / 3600, 2)
    #     count = len(RunStarts) * len(RunSites)
    #     timingRecord.write(Season+" took "+str(diff)+" hours to finish "+str(count)+" Gnome runs")
    OutDir.close
    # timingRecord.close

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == '__main__':
    import Setup_TAP as tap    
    main(tap.RootDir, tap.Data_Dir, tap.StartSites, tap.RunSites, tap.NumStarts,
         tap.RunStarts, tap.ReleaseLength, tap.TrajectoryRunLength, tap.StartTimeFiles,
         tap.TrajectoriesPath, tap.NumLEs, tap.MapFileName, tap.refloat,
         tap.current_files, tap.wind_files, tap.diffusion_coef, tap.model_timestep,
         tap.windage_range, tap.windage_persist, tap.OutputTimestep)