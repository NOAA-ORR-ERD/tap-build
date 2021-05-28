#!/usr/bin/env python

"""
Script to parse a TAP set-up to filter out receptor sites that are all land. Needs 
a site.txt and bna file. Makes assumptions about the TAP folder structure. 
"""


import sys, os
import numpy as np
import netCDF4

import matplotlib
import matplotlib.pyplot as plt

import shapely
from shapely.geometry import Polygon
# import fiona

from descartes.patch import PolygonPatch




def rec_sites_filter(site_file,bna_file,cubepath,cubepath_out):
    
    if not os.path.isfile(site_file):    
        raise Exception("Sitefile: %s doesn't exist"%site_file)

    if not os.path.isfile(bna_file):    
        raise Exception("BNA file: %s doesn't exist"%bna_file)
    
    if not os.path.isdir(cubepath):    
        raise Exception("Cube dir: %s doesn't exist"%cubepath)
    
    # tappath = os.path.dirname(site_file)
    site_file_name = os.path.split(site_file)[-1]
    # print(tappath)

    if os.path.isfile(os.path.join(cubepath,'recept_index.npy')):
        print('loading previously run filtered polys/index')
        recept_index_filt = np.load(os.path.join(cubepath,'recept_index.npy'))
        recept_polys_filt = np.load(os.path.join(cubepath,'recept_polys.npy'))

    else:
        print('calculating filter polys/index')
        recept_polys = get_ReceptPolys(site_file)
        bna_polys = rd_bna(bna_file)
        recept_polys_filt,recept_index_filt = filter_ReceptPolys(recept_polys,bna_polys)
               
        np.save(os.path.join(cubepath,'recept_polys.npy'),recept_polys_filt)
        np.save(os.path.join(cubepath,'recept_index.npy'),recept_index_filt)


    ### write out a new site.txt file  
    head,tail = get_site_headtail(site_file)
    sitefilenew = os.path.join(cubepath_out,site_file_name + '.new')
    write_site(sitefilenew,recept_polys_filt,head,tail)

    print('poly lennnn: ',len(recept_polys_filt))
    print('index lennnn: ',len(recept_index_filt))

    ### rewrite the netcdf files in the directory. 

    # first, parse the site.txt header for details
    tstr = head[head.find('every cube'):head.find('SEASONS')].split()
    n_seasons = int(tstr[-1])
    tstr = head[head.find('PICT'):head.find('SPILLS')].split()
    n_spills = int(tstr[-1])
    tstr = head[head.find('TIMES')-16:head.find('TIMES')].split()
    n_times = int(tstr[-1])
    
    print(n_seasons,n_spills,n_times)

    qq = list(find_all(head,'"'))
    file_prefix = head[qq[16]+1:qq[17]]

    season_names = []    
    for ii in range(n_seasons):
        tg = 18 + ii*6
        season_names.append(head[qq[tg]+1:qq[tg+1]])

   
    # new dir for filtered cube files
    if not os.path.isdir(cubepath_out):
        os.mkdir(cubepath_out)

    # loop through all the season dirs
    for season in season_names:
        spath = os.path.join(cubepath,season)
        print(spath)
        cubefiles = os.listdir(spath)
        print(cubefiles)

        # make new dir for TAPDATA/this season
        new_path = os.path.join(cubepath_out,season)
        if not os.path.isdir(new_path):
            os.mkdir(new_path)

        for cubefile in cubefiles:
            if cubefile[-4:] == '.bin':
                print(cubefile)
                cube = np.fromfile(os.path.join(spath,cubefile),dtype=np.float32)
       
                n_recept = int(len(cube)/n_times/n_spills)
                cube = cube.reshape(n_times, n_recept, n_spills)     

                cube_filt = cube[:,recept_index_filt,:]      

                # cubefile_filt = cubefile[:-3] + '_filt.bin'
                cube_filt.tofile(os.path.join(new_path,cubefile))




def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def filter_ReceptPolys(recept_polys,bna_polys):
    """
    checks if a receptor poly is wholly within a bna poly. If it is, it isn't kept.
    """
    
    recept_polys_new = []
    recept_index = []

    for kk in range(len(recept_polys)):
        keep = True
        bb = 0
        bna = []
        for bpoly in bna_polys[1:]:
            #print('bb: ',bb)
            bb += 1
            if recept_polys[kk].within(bpoly):
                keep = False
                break
         
        if keep:
            # print('kk:: ',kk)
            recept_polys_new.append(recept_polys[kk])
            recept_index.append(kk)

    return recept_polys_new,recept_index

def get_ReceptPolys(site_name):
    """
    grabs the receptor sites from a site.txt file. Returns as a Shapely Polygons
    """
    
    sitefile = open(site_name,'r')
    polys = []

    lines = sitefile.readlines()
    cc = 0
    for line in lines:
        cc += 1
        if "SITES" in line:
            break
    nsites = int(line.split()[0])
    print(nsites)

    for nn in range(nsites):
        npts = int(lines[cc].split('"')[-1].strip(','))
        
        points = []
        for range(cc+1,cc+npts+1):
            lon,lat = [float(i) for i in (lines[cc+1].strip().split('//')[0].strip().split(','))]
            points.append([lon,lat])

        poly = Polygon(points)   
        polys.append(poly)
        cc += npts

    sitefile.close()
    return polys

    # for line in sitefile:   # skip header info
    #     # print(line)
    #     if "SITES" in line:      
    #         break
    # nsites = int(line.split()[0])
    # print(nsites)

    # # for line in sitefile.readline():
    # for line in sitefile:
    #     if 'CUBES' in line: 
    #         break

    #     site_num = int(line.split('"')[1].strip('#')) - 1   # zero based index
    #     npts = int(line.split('"')[-1].strip(','))
    #     points = []
    #     for ii in range(npts):
    #         lon, lat = [float(i) for i in readline_clean(sitefile).split(',')]
    #         points.append([lon,lat])
          
    #     poly = Polygon(points)
    #     # poly = Feature(geometry=Polygon([poly]), site_num=site_num)
    #     polys.append(poly)


    # sitefile.close()
    # return polys

def GetNextBNAPolygon(f):
    """
    Ported from gnome.utilities.file_tools

    Utility function that returns the next polygon from a BNA file

    returns: (points, poly_type, name, sname) where:
        points:    Nx2numpy array of floats with the points
        poly_type: one of "point", "line", "poly"
        name:      name defined in the BNA
        sname:     secondary name defined in the BNA

    NOTE: It is the BNA standard to duplicate the first and last points.
          In that case, the duplicated last point is removed.

           "holes" in polygons are not supported in this code.
    See:
       http://www.softwright.com/faq/support/boundary_file_bna_format.html

    NOTE: This code doesn't allow extra spaces around the commas in the
          header line.
          If there are no commas allowed in the name, it would be easier to
          simply split on the commas
          (or march through the line looking for the quotes -- regex?)
    """
    while True: # skip blank lines
        header = f.readline()
        if not header: # end of file
            return (None,) * 4
        if header.strip(): # found a header
            break
        else:
            continue
    try:
        fields = header.split('"')
        name = fields[1]
        sname = fields[3]
        num_points = int(fields[4].strip()[1:])
        #header = header.replace('", "', '","') # some bnas have an extra space
        #name, rest = header.strip().split('","')
    except (ValueError, IndexError):
        raise ValueError('something wrong with header line: {0}'
                         .format(header))

    if num_points < 0 or num_points == 2:
        poly_type = 'polyline'
        num_points = abs(num_points)
    elif num_points == 1:
        poly_type = 'point'
    elif num_points > 2:
        poly_type = 'polygon'
    else:
        raise BnaError("polygon {0} does not have a valid number of points"
                       .format(name))

    points = []
    for i in range(num_points):
        points.append([float(j) for j in f.readline().split(',')])

    if poly_type == 'polygon':  # first and last points should be duplicated in geojson
        if points[0] != points[-1]:
            points.append(points[0])

    return (points, poly_type, name, sname)


def rd_bna(bnaFile):
    """
    Read and return BNA polygons as Shapely Polygons.
    """
    fp = open(bnaFile)
    points, poly_type, name, sname = GetNextBNAPolygon(fp)  # first read to get bounding box
    
    polys = [Polygon(points)]
  
    while True:
        points, poly_type, name, sname = GetNextBNAPolygon(fp)
        
        if points is None:
            break
        if poly_type == "polygon":  # only do polygons for now
            # check orientation -- geojson wants "right hand rule"
            if is_clockwise(points):
                # print("poly is clockwise -- reversing")
                points.reverse()
            else:
                print("poly is already counter-clockwise")
            if points[0] != points[-1]:
                print("Endpoints not equal", points[0], points[-1])
            ptype = "land" if sname == "1" else "lake"  # maybe not right, but there is something like that...
            poly = Polygon(points)
            
            # geo_poly = Feature(geometry=Polygon([points]), poly_type=ptype)
            polys.append(poly)
    
    # geojson.dump(FeatureCollection(polys), outfile, indent=2)
    fp.close
    return polys

def get_site_headtail(site_file):
    """
    Get header and footer from site.txt file. Using specific "sites" and "CUBES" strings to parse everything
    but the receptor site data
    """
    s_file = open(site_file,'r')
        
    # read it all in
    site_text = s_file.read()

    # parse to save header and footer
    htag = site_text[0:site_text.find('SITES')].rfind('\n') # last newline before 'SITES'
    head = site_text[:htag+1]
    
    ttag = site_text[0:site_text.find('CUBES')].rfind('\n') # last newline before 'CUBES'
    tail = site_text[ttag+1:]
    
    s_file.close()
    
    return head,tail

def write_site(site_name,rec_polys,head,tail):
    """
    Write out a new site.txt file. Uses the same header and footer from the previous site.txt, but only 
    writes out the receptor sites that are needed
    """
    
    num_sites = len(rec_polys)     
    file = open(site_name,'w')
    
    # header 
    file.write(head)
    
    file.write("%i SITES // number of sites\n"%num_sites)

    for polynum in range(len(rec_polys)):
        pts = np.asarray(rec_polys[polynum].exterior.coords[:])
        file.write('"#%i","1",5\n'%(polynum+1))   
        file.write('%11.6f, %11.6f\n'%(pts[0][0], pts[0][1])) 
        file.write('%11.6f, %11.6f\n'%(pts[1][0], pts[1][1])) 
        file.write('%11.6f, %11.6f\n'%(pts[2][0], pts[2][1])) 
        file.write('%11.6f, %11.6f\n'%(pts[3][0], pts[3][1])) 
        file.write('%11.6f, %11.6f\n'%(pts[4][0], pts[4][1])) 
    
    # tail
    file.write(tail)
    
    file.close()
    return

    
def is_clockwise(poly):
    """
    returns True if the polygon is clockwise ordered, false if not

    expects a sequence of tuples, or something like it (Nx2 array for instance),
    of the points:

    [ (x1, y1), (x2, y2), (x3, y3), ...(xi, yi) ]

    See: http://paulbourke.net/geometry/clockwise/
    """

    total = poly[-1][0] * poly[0][1] - poly[0][0]*poly[-1][1] # last point to first point
    for i in range(len(poly)-1):
        total += poly[i][0] * poly[i+1][1] - poly[i+1][0]*poly[i][1]

    if total <= 0:
        return True
    else:
        return False

def readline_clean(fp):
    """
    reads a line, striping off the comments and whitespace
    """
    return fp.readline().strip().split('//')[0].strip()



if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        raise Exception("Must define path/filename for TAP sitefile")
    
    site_file = sys.argv[1]   
    if not os.path.isfile(sys.argv[1]):    
        raise Exception("Sitefile: %s doesn't exist"%site_file)


    if len(sys.argv) < 3:
        raise Exception("Must define path/filename for bna file")
    
    bna_file = sys.argv[2]    
    if not os.path.isfile(sys.argv[2]):    
        raise Exception("BNA file: %s doesn't exist"%bna_file)

    print('site file:: ',site_file)
    
    rec_sites_filter(site_file,bna_file,cubepath,cubepath_out)
