#!/usr/bin/env python

from netCDF4 import Dataset
import numpy as np
import progressbar as pb
import argparse

def calc_stats():

    parser = argparse.ArgumentParser(description='Calculate Statistics on NetCDF Files.')

    parser.add_argument('filename', metavar='f', type=str,
                        help='Path of a netcdf file (File Extension = .nc).')

    parser.add_argument('variable', metavar='v', type=str,
                        help='Name of the variable in the netcdf file to process.')

    parser.add_argument('-t', dest='timestep', help="Isolates a timestep from file", )
    parser.add_argument('-x', dest='x_coor', help="Specify an x coordinate to run statistics on ")
    parser.add_argument('-y', dest='y_coor', help="Specify an y coordinate to run statistics on ")

    args = parser.parse_args()

    print "Processing netCDF statistics...\n"
    print "Filename: {0}".format(args.filename)

    #Open data set
    ds = Dataset(args.filename, 'r')
    f = ds.variables[args.variable]

    #collect important info create arrays
    nt,nx,ny = np.shape(f)
    maxes = []
    mins = []
    means = []

    #Create a progress bar to info the user
    bar = pb.ProgressBar(max_value=nt)

    #Check what the user wants. Always output basin wide/all time results
    operations = ['maximum','minimum','average']
    data_description = ['All time']

    #User requested a specific timestep
    #if timestep !=None and x_coor == None and y_coor == None:
    # Always show the user the whole basin and through all time.
    img = f[:,:,:]
    maxes.append(np.max(img))
    mins.append(np.min(img))
    means.append(np.average(img))

    #User requested single row for all timesteps
    if args.timestep == None and args.x_coor != None and args.y_coor == None:
        data_description.append('At X={0}'.format(args.x_coor))
        img = f[:,:,args.x_coor]
        maxes.append(np.max(img))
        mins.append(np.min(img))
        means.append(np.average(img))

    #User requested single column for all timesteps
    if args.timestep == None and args.x_coor == None and args.y_coor != None:
        data_description.append('At Y={0}'.format(args.y_coor))
        img = f[:,args.y_coor,:]
        maxes.append(np.max(img))
        mins.append(np.min(img))
        means.append(np.average(img))

    #User requested single point for all timesteps
    if args.timestep == None and args.x_coor != None and args.y_coor != None:
        data_description.append('At X={0}, Y={1}'.format(args.x_coor,args.y_coor))
        img = f[:,args.y_coor,args.x_coor]
        maxes.append(np.max(img))
        mins.append(np.min(img))
        means.append(np.average(img))

    if args.timestep != None and args.x_coor != None and args.y_coor != None:
        data_description.append('At T={0},X={1}, Y={2}'.format(args.timestep,args.x_coor,args.y_coor))
        img = f[args.timestep,args.y_coor,args.x_coor]
        maxes.append(np.max(img))
        mins.append(np.min(img))
        means.append(np.average(img))


    ds.close()
    msg_str =  " "*3 + "NetCDF statistics" + " "*3

    print "="*len(msg_str)
    print msg_str
    print "="*len(msg_str)
    print ""
    #Output to screen
    for i,s in enumerate(data_description):
        print "{0} maximum {1}: {2}".format(s,args.variable,maxes[i])
        print "{0} minimum {1}: {2}".format(s,args.variable,mins[i])
        print "{0} average {1}: {2}\n".format(s,args.variable,means[i])


if __name__ == '__main__':
    calc_stats()
