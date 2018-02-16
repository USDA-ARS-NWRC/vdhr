#!/usr/bin/env python

from netCDF4 import Dataset
import numpy as np
import progressbar as pb
import argparse
import os
from collections import OrderedDict

def calc_stats(img, non_zero = False):
    '''
    args:
        img: a numpy array of any dimension and size
        non_zero: Calculate stats not including zero (defaults false)
    returns:
        result: dictionary containing max, min, avg standard deviation
    '''
    result = OrderedDict()
    if non_zero:
        img_id = img!=0.0
    else:
        img_id = img==img

    result['maximum'] = np.max(img[img_id])
    result['minimum'] = np.min(img[img_id])
    result['avgerage'] = np.average(img[img_id])
    result['standard deviation'] = np.std(img[img_id])
    return result

def return_img_and_message(img,dimension_value):

    if dimension_value == None:
        value_str = "All"
        img = img[:]
    else:
        value_str = dimension_value
        img = img[dimension_value]

    data_description = "{0} = {1}".format(name,value_str)
    return img,data_description

def main():

    parser = argparse.ArgumentParser(description='Calculate Statistics on NetCDF Files.')

    parser.add_argument('filename', metavar='f', type=str,
                        help='Path of a netcdf file (File Extension = .nc).')

    parser.add_argument('variable', metavar='v', type=str,
                        help='Name of the variable in the netcdf file to process.')

    parser.add_argument('-t', dest='timestep', help="Isolates a timestep from file", )
    parser.add_argument('-x', dest='x_coor', help="Specify an x coordinate to run statistics on ")
    parser.add_argument('-y', dest='y_coor', help="Specify an y coordinate to run statistics on ")
    parser.add_argument('-nz', dest='non_zero', action='store_true', help="Disables any zero from being the min value")

    args = parser.parse_args()
    filename = os.path.abspath(os.path.expanduser(args.filename))
    if not os.path.isfile(filename):
        print("File Does not exist. {0}".format(filename))
        sys.exit()

    print "Processing netCDF statistics...\n"
    print "Filename: {0}".format(filename)

    #Open data set
    ds = Dataset(filename, 'r')
    f = ds.variables[args.variable]

    #collect important info create arrays
    nt,nx,ny = np.shape(f)

    #Create a progress bar to info the user
    bar = pb.ProgressBar(max_value=nt)

    #Use an dict to store stats for easy recall
    data = OrderedDict()

    # Always show the user the whole basin and through all time.
    img = f[:,:,:]
    data['Entire Image Domain'] = calc_stats(img,args.non_zero)

    #Check what the user wants. Always output basin wide/all time results
    data_description = 'At '

    if args.timestep != None or args.y_coor !=None or args.x_coor != None:

        for arg in [args.timestep,args.y_coor,args.x_coor]:
            img,msg = return_index_and_message(img,arg)
            data_description += msg


        data[data_description] = calc_stats(new_img, non_zero = args.non_zero)


    msg_str =  " "*3 + "NetCDF statistics" + " "*3

    print "="*len(msg_str)
    print msg_str
    print "="*len(msg_str)
    print ""
    print "Total Time Steps = {0}".format(nt)
    print "Total Number of Columns = {0}".format(nx)
    print "Total Number of Rows = {0}".format(ny)
    print ""

    #Output to screen
    for k,v in data.items():
        for description,value in v.items():
            print "{0}: {1}".format(description,value)



    ds.close()
if __name__ == '__main__':
    main()
