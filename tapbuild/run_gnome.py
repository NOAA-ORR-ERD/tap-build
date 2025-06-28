#!/usr/bin/env python

"""
In this stage, the main loops are gone though to run a pygnome model.

Parameters for that model are
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from .utilities import load_config, read_start_times_file

import gc  # garbage collector

import gnome.scripting as gs
# def main(RootDir, StartSites, RunSites, NumStarts, RunStarts, ReleaseLength,
#          TrajectoryRunLength, StartTimeFiles, TrajectoriesPath, NumLEs, MapFileName,
#          refloat, current_files, wind_files, diffusion_coef, model_timestep,
#          windage_range, windage_persist, OutputTimestep,VariableMass,waterTemp,waterSal,SpillAmount):

def run_gnome(config_file):

    print("loading: ", config_file)
    config = load_config(config_file)

    # convert paths:
    config.RootDir = Path(config.RootDir)
    config.TrajectoriesPath = Path(config.TrajectoriesPath)

    print(f"{config.pygnome_script=}")

    model_runner = load_config(config.pygnome_script)

    # timingRecord = open(os.path.join(RootDir,"timing.txt"),"w")
    # count = len(StartTimeFiles) * len(RunStarts) * len(RunSites)
    # timingRecord.write("This file tracks the time to process "+str(count)+" gnome runs")

    # make the model now, unless config says to re-initialize each run.
    model = None if config.re_initialize_model else model_runner.initialize_model(config)

    for season in config.Seasons:
        season_name = season[0]

        stfilename = config.RootDir / f"{season_name}Starts.txt"
        for pos_idx, start_site in enumerate(config.StartSites):
            out_dir = config.TrajectoriesPath / season_name / f'pos_{(pos_idx+1):03d}'
            out_dir.mkdir(parents=True, exist_ok=True)

            start_coords = start_site['start_position']

            for time_idx, start_time in enumerate(read_start_times_file(stfilename, config.NumStarts)):
                # make the dir for the output
                (config.RootDir / config.TrajectoriesPath / season_name).mkdir(parents=True,exist_ok=True)
                print(f"about to run PyGNOME for {season_name}: {start_coords}: {start_time}")

                start_site['start_time'] = start_time
                start_site['run_duration'] = timedelta(hours=config.TrajectoryRunLength)
                start_site['release_duration'] = timedelta(hours=config.ReleaseLength)
                start_site['output_timestep'] = timedelta(hours=config.OutputTimestep)
                
                netcdf_output_file = (out_dir / ('pos_%03i-t%03i_%08i.nc'
                                                  %(pos_idx+1, time_idx, int(start_time.strftime('%y%m%d%H'))))
                                                  )
                if netcdf_output_file.exists:
                    print('Already ran this one')

                
                else:

                    model = model_runner.initialize_model(config) if model is None  or config.re_initialize_model else model

                    # build the NetCDF outputter
                    model = model_runner.setup_for_run(model, config, start_site)


                    model.outputters.clear()
                    model.outputters += gs.NetCDFOutput(netcdf_output_file,
                                                        output_timestep=timedelta(hours=config.OutputTimestep),
                                                        surface_conc=None)

                    if not config.re_initialize_model:
                        gc.collect()
                        
                    model.full_run()


#     # model timing
#     release_duration = timedelta(hours=ReleaseLength)
#     run_time = timedelta(hours=TrajectoryRunLength)

#     # initiate model
#     model = gs.Model(duration=run_time,
#                   time_step=model_timestep,
#                   uncertain=False)

#     # determine boundary for model
#     print("Adding the map:",MapFileName)
#     # mapfile = get_datafile(MapFileName)
#     model.map = gs.MapFromBNA(MapFileName, refloat_halflife=refloat)

#     # get time details for forcing files
#     Time_MapC = get_Time_MapC(current_files)
#     Time_MapW = get_Time_MapW(wind_files)

#     # loop through seasons
#     for Season in StartTimeFiles:
#         # timer1 = datetime.now()

#         SeasonName = Season[1]
#         start_times = open(Season[0],'r').readlines()[:NumStarts]
#         make_dir(os.path.join(RootDir,TrajectoriesPath,SeasonName))
#         print("  Season: ",SeasonName)

#         # get and parse start times in this season
#         start_dt = []
#         for start_time in start_times:
#             start_time = [int(i) for i in start_time.split(',')]
#             start_time = datetime(start_time[0],start_time[1],start_time[2],start_time[3],start_time[4])
#             start_dt.append(start_time)

#         ## loop through start times
#         for time_idx in RunStarts:
#             # timer2 = datetime.now()

#             gc.collect()
#             model.movers.clear()
#             model.environment.clear()
#             model.weatherers.clear()

#             ## set the start time
#             start_time = start_dt[time_idx]
#             end_time = start_time + run_time
#             model.start_time = start_time
#             print("  ",start_time," to ",end_time)


#             # set up the model with the correct forcing files for this time/duration
#             file_list_c = get_file_list(start_time,end_time,Time_MapC)
#             file_list_w = get_file_list(start_time,end_time,Time_MapW)


#             print('number of ROMS files :: ', len(file_list_c))
#             print(file_list_c)

#             print('number of wind files :: ', len(file_list_w))
#             print(file_list_w)

#             # print('creating curr MFDataset')
#             # ds_c = nc4.MFDataset(file_list_c)
#             print('adding a CurrentMover (Trapeziod/RK4):')
#             g_curr = gs.GridCurrent.from_netCDF(filename=file_list_c,
#                                     # dataset=ds_c,
#                                     # grid_topology={'node_lon':'lonc','node_lat':'latc'}
#                                     )
#             c_mover = gs.CurrentMover(current=g_curr, default_num_method='RK4')
#             model.movers += c_mover

#             # print('creating wind MFDataset')
#             # ds_w = nc4.MFDataset(file_list_w)
#             print('adding a WindMover (Euler):')
#             g_wind = gs.GridWind.from_netCDF(filename=file_list_w,
#                                     # dataset=ds_w,
#                                     # grid_topology={'node_lon':'lonc','node_lat':'latc'}
#                                     )
#             w_mover = gs.WindMover(wind = g_wind, default_num_method='Euler')
#             model.movers += w_mover

#             ## add diffusion
#             model.movers += gs.RandomMover(diffusion_coef=diffusion_coef)

#             if VariableMass:
#                 model.environment += g_wind
#                 water = gs.Water(temperature=waterTemp,salinity=waterSal)
#                 waves = gs.Waves(g_wind)
#                 model.weatherers += Evaporation(water=water,wind=g_wind)
#                 model.weatherers += NaturalDispersion(waves=waves)


#             ## loop through start locations
#             for pos_idx in RunSites:
#                 # timer3 = datetime.now()

#                 start_position = [float(i) for i in StartSites[pos_idx][0].split(',')]
#                 print(start_position)
#                 start_OilType = None
#                 spill_amount = None
#                 spill_units = None
#                 if VariableMass:
#                     start_OilType = StartSites[pos_idx][1]
#                     start_OilFile = StartSites[pos_idx][3]
#                     spill_amount = SpillAmount[0]
#                     spill_units = SpillAmount[1]

#                 OutDir = os.path.join(RootDir,TrajectoriesPath,SeasonName,'pos_%03i'%(pos_idx+1))
#                 make_dir(OutDir)

#                 print("    ",pos_idx,time_idx)
#                 print("    Running: start time:",start_time)
#                 print("      at start location: ",start_position)
#                 print("      with oil ",start_OilFile)

#                 ## set the spill to the location
#                 spill = gs.surface_point_line_spill(num_elements=NumLEs,
#                                                  start_position=(start_position[0], start_position[1], 0.0),
#                                                  release_time=start_time,
#                                                  end_release_time=start_time+release_duration,
#                                                 #  windage_range=windage_range,
#                                                 #  windage_persist=windage_persist,
#                                                  substance=gs.GnomeOil(filename=start_OilFile),
#                                                  amount=spill_amount,
#                                                  units=spill_units)

#                 # print "adding netcdf output"
#                 netcdf_output_file = os.path.join(OutDir,'pos_%03i-t%03i_%08i.nc'
#                                                   %(pos_idx+1, time_idx,int(start_time.strftime('%y%m%d%H'))),
#                                                   )
#                 model.outputters.clear()
#                 model.outputters += NetCDFOutput(netcdf_output_file,output_timestep=timedelta(hours=OutputTimestep),surface_conc=None)

#                 model.spills.clear()
#                 model.spills += spill

#                 model.full_run(rewind=True)

#     #             timer4 = datetime.now()
#     #             diff = round((timer4-timer3).total_seconds() / 60, 2)
#     #             timingRecord.write("\t\t"+str(pos_idx)+" took "+str(diff)+" minutes to complete")
#     #         diff = round((timer4-timer2).total_seconds() / 3600, 2)
#     #         count = len(RunSites)
#     #         timingRecord.write("\t"+str(time_idx)+" took "+str(diff)+" hours to finish "+str(count)+" Gnome runs")
#     #     diff = round((timer4-timer1).total_seconds() / 3600, 2)
#     #     count = len(RunStarts) * len(RunSites)
#     #     timingRecord.write(Season+" took "+str(diff)+" hours to finish "+str(count)+" Gnome runs")
#     # OutDir.close
#     # timingRecord.close

# def make_dir(path):
#     if not os.path.exists(path):
#         os.makedirs(path)

# def get_Time_MapC(file_list):
#     Time_Map = []
#     for fn in file_list:
#         # d = nc4.Dataset(fn)
#         # t = d['time']
#         # file_start_time = nc4.num2date(t[0], units=t.units)
#         print(fn)
#         gcur = gs.GridCurrent.from_netCDF(fn)
#         file_start_time = gcur.time.data[0]
#         Time_Map.append( (file_start_time, fn) )
#     return Time_Map

# def get_Time_MapW(file_list):
#     Time_Map = []
#     for fn in file_list:
#         print(fn)
#         gwin = gs.GridWind.from_netCDF(fn)
#         file_start_time = gwin.time.data[0]
#         Time_Map.append( (file_start_time, fn) )
#     return Time_Map

# def get_file_list(start_time,end_time,Time_Map):
#     file_list = []
#     i = 0
#     for i in range(0, len(Time_Map) - 1):
#         curr_t, curr_fn = Time_Map[ i ]
#         next_t, next_fn = Time_Map[ i+1 ]
#         if next_t > start_time:
#             file_list.append( curr_fn )
#             if next_t > end_time:
#                 break
#     file_list.append( next_fn )    # pad the list with next file to cover special case of last file.
#                                    #   awkward. fix later
#     return file_list


if __name__ == '__main__':
    run_gnome(sys.argv[1])

    # main(tap.RootDir, tap.StartSites, tap.RunSites, tap.NumStarts,
    #      tap.RunStarts, tap.ReleaseLength, tap.TrajectoryRunLength, tap.StartTimeFiles,
    #      tap.TrajectoriesPath, tap.NumLEs, tap.MapFileName, tap.refloat,
    #      tap.current_files, tap.wind_files, tap.diffusion_coef, tap.model_timestep,
    #      tap.windage_range, tap.windage_persist, tap.OutputTimestep,
    #      tap.VariableMass,tap.waterTemp,tap.waterSal,tap.SpillAmount)
