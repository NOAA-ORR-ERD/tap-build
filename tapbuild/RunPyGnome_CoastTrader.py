#!/usr/bin/env python

import os
from datetime import datetime, timedelta

import gnome.scripting as gs
from gnome.outputters import NetCDFOutput

# from gnome.environment import GridCurrent, GridWind, Water, Waves
# from gnome.movers import GridCurrentMover, GridWindMover
from gnome.weatherers import Evaporation, NaturalDispersion

import netCDF4 as nc4
import gc  # garbage collector

grid_file = "/Users/rachael.mueller/Projects/SpillScenarioFiles/2024/CoastTrader/model_input/WCOFS_current/grd_cutout_Rachael.nc" 
def main(
    RootDir,
    StartSites, 
    RunSites, 
    NumStarts, RunStarts, ReleaseLength,
    TrajectoryRunLength, StartTimeFiles, TrajectoriesPath, 
    NumLEs, MapFileName, refloat, current_files, wind_files, oil_file, 
    diffusion_coef, model_timestep, windage_range, windage_persist, 
    OutputTimestep,VariableMass,waterTemp,waterSal,SpillAmount):
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
    # Time_MapC = get_Time_MapC(current_files)
    # Time_MapW = get_Time_MapW(wind_files) # for list of files
        
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
        print(RunStarts, ": ", start_time)
        ## loop through start times
        for time_idx in RunStarts:
            print(time_idx)
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
            # file_list_c = get_file_list(start_time,end_time,Time_MapC)
            file_list_w = wind_files # one file
            # file_list_w = get_file_list(start_time,end_time,Time_MapW) # multiple files


            #print('number of ROMS files :: ', len(file_list_c))
            #print(file_list_c)
        
            print('number of wind files :: ', len(file_list_w))
            print(file_list_w)
            
            # print('creating curr MFDataset')
            # ds_c = nc4.MFDataset(file_list_c)
            print('adding a CurrentMover (Trapeziod/RK4):')
            # print(f" Current file: {current_files}")
            g_curr = gs.GridCurrent.from_netCDF(
                         data_file = current_files, #file_list_c,
                         grid_file = grid_file
            )
            c_mover = gs.CurrentMover(
                          current=g_curr, default_num_method='RK4'
            )
            model.movers += c_mover

            # print('creating wind MFDataset')
            # ds_w = nc4.MFDataset(file_list_w)
            print('adding a WindMover (Euler):')
            g_wind = gs.GridWind.from_netCDF(
                filename=file_list_w
            )
            w_mover = gs.WindMover(
                wind = g_wind, 
                default_num_method='Euler'
            )
            model.movers += w_mover
            
            ## add diffusion
            model.movers += gs.RandomMover(diffusion_coef=diffusion_coef)
            
            if VariableMass:
                model.environment += g_wind
                water = gs.Water(temperature=waterTemp,salinity=waterSal)
                waves = gs.Waves(g_wind)
                model.weatherers += Evaporation(water=water,wind=g_wind)
                model.weatherers += NaturalDispersion(waves=waves)
                model.add_weathering()

            ## loop through start locations
            for pos_idx in RunSites:
                
                start_position = [float(i) for i in StartSites[pos_idx][0].split(',')]
                print(start_position)
                start_OilType = None
                spill_amount = None
                spill_units = None
                # if VariableMass:
                #     start_OilType = StartSites[pos_idx][1]
                #     start_OilFile = StartSites[pos_idx][3]
                spill_amount = SpillAmount[0]
                spill_units = SpillAmount[1]

                OutDir = os.path.join(RootDir,TrajectoriesPath,SeasonName,'pos_%03i'%(pos_idx+1))
                make_dir(OutDir)
                
                print("    ",pos_idx,time_idx)
                print("    Running: start time:",start_time)
                print("      at start location: ",start_position)
                print("Spill amount ",spill_amount)
                print("num elements", NumLEs) 
                ## set the spill to the location
                if VariableMass:
                    spill = gs.surface_point_line_spill(
                        num_elements=NumLEs,
                        start_position=(
                            start_position[0], 
                            start_position[1], 0.0
                        ),
                        release_time=start_time,
                        end_release_time=start_time+release_duration,
                        amount=spill_amount,
                        units=spill_units,
                        substance = gs.GnomeOil(filename=oil_file)
                    )
                else:
                    spill = gs.surface_point_line_spill(
                        num_elements=NumLEs,
                        start_position=(
                            start_position[0], 
                            start_position[1], 0.0
                        ),
                        release_time=start_time,
                        end_release_time=start_time+release_duration,
                        amount=spill_amount,
                        units=spill_units
                    )
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

def get_Time_MapC(file_list):
    Time_Map = []
    for fn in file_list:
        print(fn)
        print(grid_file)
        # d = nc4.Dataset(fn)
        # t = d['time']
        # file_start_time = nc4.num2date(t[0], units=t.units)
        gcur = gs.GridCurrent.from_netCDF(
            data_file = fn,
            grid_file = grid_file
        )
        #gcur = gs.GridCurrent.from_netCDF(fn)
        file_start_time = gcur.time.data[0]
        Time_Map.append( (file_start_time, fn) )
        print("~~~~~~~~Time_Map ~~~~~~~~~~")
        print(Time_Map)
    return Time_Map

def get_Time_MapW(file_list):
    Time_Map = []
    for fn in file_list:
        print(fn)
        gwin = gs.GridWind.from_netCDF(fn)
        file_start_time = gwin.time.data[0]
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
         tap.current_files, tap.wind_files, tap.oil_file, tap.diffusion_coef, tap.model_timestep,
         tap.windage_range, tap.windage_persist, tap.OutputTimestep,
         tap.VariableMass,tap.waterTemp,tap.waterSal,tap.SpillAmount)
