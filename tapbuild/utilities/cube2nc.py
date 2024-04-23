#!/usr/bin/env python3

"""
Read in a binary format cube, and write out a netCDF4 file

"""

import sys, os
import numpy as np
import netCDF4 as nc


def cube2nc(binFile,ncFile,times,n_runs):

    # load data froom binary cube file	
    cubeDat = np.fromfile(binFile,dtype=np.float32)
    n_cells = int(len(cubeDat)/len(times)/n_runs)
    print(n_cells)
    cubeDat = cubeDat.reshape(len(times),n_cells,n_runs)

    ncDat = nc.Dataset(ncFile,'w')
    ncDat.createDimension('t',None)
    ncDat.createDimension('ncells',n_cells)
    ncDat.createDimension('nruns',n_runs)

    time = ncDat.createVariable('time',float,'t')
    cube = ncDat.createVariable('cube',float,('t','ncells','nruns'))

    time[:] = times
    cube[:] = cubeDat

    ncDat.close()