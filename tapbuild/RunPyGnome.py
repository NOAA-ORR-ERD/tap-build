#!/usr/bin/env python

import os
from datetime import datetime, timedelta

import gnome.scripting as gs
from gnome.outputters import NetCDFOutput

from gnome.environment import GridCurrent, GridWind, Water, Waves
# from gnome.movers import GridCurrentMover, GridWindMover
from gnome.weatherers import Evaporation, NaturalDispersion

import netCDF4 as nc4

import gc


def main(RootDir, StartSites, RunSites, NumStarts, RunStarts, ReleaseLength,
         TrajectoryRunLength, StartTimeFiles, TrajectoriesPath, NumLEs, MapFileName,
         refloat, current_files, wind_files, diffusion_coef, model_timestep,
         windage_range, windage_persist, OutputTimestep,VariableMass,waterTemp,waterSal,SpillAmount):
    
    # timingRecord = open(os.path.join(RootDir,"timing.txt"),"w")
    # count = len(StartTimeFiles) * len(RunStarts) * len(RunSites)
    # timingRecord.write("This file tracks the time to process "+str(count)+" gnome runs")
    
    # model timing
    release_duration = timedelta(hours=ReleaseLength)
    run_time = timedelta(hours=TrajectoryRunLength)
    
    # initiate model
    model = gs.Model(duration=run_time,
                  time_step=model_timestep,
                  uncertain=False)
    
    # determine boundary for model
    print("Adding the map:",MapFileName)
    # mapfile = get_datafile(MapFileName)
    model.map = gs.MapFromBNA(MapFileName, refloat_halflife=refloat)
    
    # get time details for forcing files
    Time_MapC = get_Time_Map(current_files)
    Time_MapW = get_Time_Map(wind_files)
        
    # loop through seasons
    for Season in StartTimeFiles:
        # timer1 = datetime.now()
        
        SeasonName = Season[1]
        start_times = open(Season[0],'r').readlines()[:NumStarts]
        make_dir(os.path.join(RootDir,TrajectoriesPath,SeasonName))
        print("  Season: ",SeasonName)
        
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
            model.environment.clear()
            model.weatherers.clear()
            
            ## set the start time
            start_time = start_dt[time_idx]
            end_time = start_time + run_time
            model.start_time = start_time
            print("  ",start_time," to ",end_time)
            

            # set up the model with the correct forcing files for this time/duration
            file_list_c = get_file_list(start_time,end_time,Time_MapC)
            file_list_w = get_file_list(start_time,end_time,Time_MapW)


            print('number of ROMS files :: ', len(file_list_c))
            print(file_list_c)
        
            print('number of wind files :: ', len(file_list_w))
            print(file_list_w)
            
            # # add wind movers
            # w_mover = PyWindMover(filename=file_list_w)
            # model.movers += w_mover
            
            # ## add current movers
            # c_mover = PyCurrentMover.from_netCDF(file_list)
            # model.movers += c_mover
            
            print('creating curr MFDataset')
            ds_c = nc4.MFDataset(file_list_c)
            print('adding a CurrentMover (Trapeziod/RK4):')
            g_curr = GridCurrent.from_netCDF(filename=file_list_c,
                                       # dataset=ds_c,
                                       grid_topology={'node_lon':'lonc','node_lat':'latc'})
            c_mover = gs.PyCurrentMover(current=g_curr, default_num_method='RK4')
            model.movers += c_mover

            print('creating wind MFDataset')
            ds_w = nc4.MFDataset(file_list_w)
            print('adding a WindMover (Euler):')
            g_wind = GridWind.from_netCDF(filename=file_list_w,
                                    # dataset=ds_w,
                                    grid_topology={'node_lon':'lonc','node_lat':'latc'})
            w_mover = gs.PyWindMover(wind = g_wind, default_num_method='Euler')
            model.movers += w_mover
            
            ## add diffusion
            model.movers += gs.RandomMover(diffusion_coef=diffusion_coef)
            
            if VariableMass:
                model.environment += g_wind
                water = Water(temperature=waterTemp,salinity=waterSal)
                waves = Waves(g_wind)
                model.weatherers += Evaporation(water=water,wind=g_wind)
                model.weatherers += NaturalDispersion(waves=waves)


            ## loop through start locations
            for pos_idx in RunSites:
                # timer3 = datetime.now()
                
                start_position = [float(i) for i in StartSites[pos_idx][0].split(',')]
                print(start_position)
                start_OilType = None
                spill_amount = None
                spill_units = None
                if VariableMass:
                    start_OilType = StartSites[pos_idx][1]
                    start_OilFile = StartSites[pos_idx][3]
                    spill_amount = SpillAmount[0]
                    spill_units = SpillAmount[1]

                OutDir = os.path.join(RootDir,TrajectoriesPath,SeasonName,'pos_%03i'%(pos_idx+1))
                make_dir(OutDir)
                
                print("    ",pos_idx,time_idx)
                print("    Running: start time:",start_time)
                print("      at start location: ",start_position)
                print("      with oil ",start_OilFile)
                
                ## set the spill to the location
                spill = gs.surface_point_line_spill(num_elements=NumLEs,
                                                 start_position=(start_position[0], start_position[1], 0.0),
                                                 release_time=start_time,
                                                 end_release_time=start_time+release_duration,
                                                 windage_range=windage_range,
                                                 windage_persist=windage_persist,
                                                 substance=gs.GnomeOil(start_OilFile),
                                                 amount=spill_amount,
                                                 units=spill_units)
                
                # print "adding netcdf output"
                netcdf_output_file = os.path.join(OutDir,'pos_%03i-t%03i_%08i.nc'
                                                  %(pos_idx+1, time_idx,int(start_time.strftime('%y%m%d%H'))),
                                                  )
                model.outputters.clear()
                model.outputters += NetCDFOutput(netcdf_output_file,output_timestep=timedelta(hours=OutputTimestep),surface_conc=None)
                
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
    # OutDir.close
    # timingRecord.close

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_Time_Map(file_list):
    Time_Map = []
    for fn in file_list:
        d = nc4.Dataset(fn)
        t = d['time']
        file_start_time = nc4.num2date(t[0], units=t.units)
        Time_Map.append( (file_start_time, fn) )
    return Time_Map


def get_file_list(start_time,end_time,Time_Map):    
    file_list = []
    i = 0
    for i in range(0, len(Time_Map) - 1):
        curr_t, curr_fn = Time_Map[ i ]
        next_t, next_fn = Time_Map[ i+1 ]
        if next_t > start_time:
            file_list.append( curr_fn )
            if next_t > end_time:
                break
    file_list.append( next_fn )    # pad the list with next file to cover special case of last file. 
                                   #   awkward. fix later
    return file_list


if __name__ == '__main__':
    import Setup_TAP as tap    
    main(tap.RootDir, tap.StartSites, tap.RunSites, tap.NumStarts,
         tap.RunStarts, tap.ReleaseLength, tap.TrajectoryRunLength, tap.StartTimeFiles,
         tap.TrajectoriesPath, tap.NumLEs, tap.MapFileName, tap.refloat,
         tap.current_files, tap.wind_files, tap.diffusion_coef, tap.model_timestep,
         tap.windage_range, tap.windage_persist, tap.OutputTimestep,
         tap.VariableMass,tap.waterTemp,tap.waterSal,tap.SpillAmount)