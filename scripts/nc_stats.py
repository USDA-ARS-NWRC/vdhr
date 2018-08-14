#!/usr/bin/env python

from netCDF4 import Dataset
import numpy as np
import progressbar as pb
import argparse
from collections import OrderedDict
import sys


def calc_stats():

    parser = argparse.ArgumentParser(description='Calculate Statistics on NetCDF Files.')

    parser.add_argument('filename', metavar='f', type=str,
                        help='Path of a netcdf file (File Extension = .nc).')

    parser.add_argument('variable', metavar='v', type=str,
                        help='Name of the variable in the netcdf file to process.')

    parser.add_argument('-t', dest='time', help="Isolates a timestep from file", default = 'all')
    parser.add_argument('-x', dest='x', help="Specify an x coordinate to run statistics on ", default = 'all')
    parser.add_argument('-y', dest='y', help="Specify an y coordinate to run statistics on ", default = 'all')

    args = parser.parse_args()

    #Open data set
    ds = Dataset(args.filename, 'r')
    print("\n=========== NC_STATS v0.1.0 ==========")
    print("\nProcessing netCDF statistics...")
    print("\tFilename: {0}".format(args.filename))
    print("\tvariable: {0}".format(args.variable))

    # Build our basic operations list
    base_dict = OrderedDict({})
    operations = ['max','min','average']
    for o in operations:
        base_dict[o] = None

    # Always output stats on full dimension of the data
    data_description = OrderedDict()
    description = None

    # Check user inputs
    for i,d in enumerate(ds.dimensions.keys()):
        if hasattr(args,d.lower()):
            a = getattr(args,d.lower())

            if a != 'all':

                # Confirm user provided number
                try:
                    a = float(a)
                except:
                    print("Please use numbers for {0} dimension".format(d))


                if a not in ds.variables[d][:]:
                    print("{0} = {1} is not the in the data domain!".format(d,a))
                    print(ds.variables[d][:])
                    sys.exit()

            # Form a description of data requested
            if i==0:
                description = "{0}={1}".format(d,a)
            else:
                description += ", {0}={1}".format(d,a)

    # If a description was formed, add it to our data to be processed
    if description != None:
        data_description[description] = base_dict.copy()

    # Perform all calcs
    for op in operations:
        fn = getattr(np,op)

        # Cycle through all the requested data
        print("")
        print(" Calculating {0} of {1} for:".format(op, args.variable))
        for desc, data in data_description.items():
            # User requested single row for all timesteps
            print("\t{0}".format(desc.lower()))

            if desc == 'all time':
                data_description[desc][op] = fn(ds.variables[args.variable][:])

            else:
                ind_str = desc.split(',')
                ind = ""

                #Form a string indice to use
                for i,z in enumerate(ind_str):
                    d = z.split('=')

                    if d[-1] == 'all':
                        c = ":"
                    else:
                        c = d[-1]

                    if i == 0:
                        ind += c
                    else:
                        ind += ","+c

                data_description[desc][op] = eval('fn(ds.variables[args.variable][{0}])'.format(ind))

    ds.close()
    msg_str =  " "*3 + "NetCDF statistics" + " "*3
    print('')
    print("="*len(msg_str))
    print(msg_str)
    print("="*len(msg_str))
    #Output to screen
    for k,ops in data_description.items():
        print('')
        for op,value in ops.items():
            print("{0} {1} for {2}: {3:0.4f}".format(args.variable,op,k,value))
    print("")

if __name__ == '__main__':
    calc_stats()
