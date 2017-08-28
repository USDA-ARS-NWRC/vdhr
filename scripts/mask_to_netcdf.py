from netCDF4 import Dataset
import numpy as np
import argparse
import os

#Convert an ascii file to netcdf
parser = argparse.ArgumentParser()

parser.add_argument("ascii_file", type=str,
                    help="Full filename for ascii file to convert.")

parser.add_argument("-o","--output_netcdf", type=str,
                    help="""Full file path to output file. If none is provided, the
                    filename is the same as the ascii file but in current directory and
                    with the netcdf file extension.""",
                    default=None)


args = parser.parse_args()

#parse the header
with open(args.ascii_file) as f:
    i = 0
    txt = f.readline()
    data = txt.split('\t')
    hdata = {}

    while len(data) == 2:
        txt = f.readline()
        hdata[data[0]] = int(data[1])
        data = txt.split('\t')
        i+=1
    f.close()

ascii_data = np.genfromtxt(args.ascii_file,skip_header=i)

#Parse the option name
if args.output_netcdf is None:
    #Isolate the name of the input file and use it for netcdf
    out_fname = (os.path.split(args.ascii_file)[-1]).split('.')[0]+'.nc'
else:
    out_fname = args.output_netcdf

output = Dataset("."+os.sep+out_fname,'w')

x = np.arange(hdata['xllcorner'], hdata['xllcorner'] + hdata["ncols"]*hdata['cellsize'], hdata['cellsize'])
y = np.arange(hdata['yllcorner'], hdata['yllcorner'] + hdata["nrows"]*hdata["cellsize"], hdata["cellsize"])

output.createDimension('x', None)
output.createDimension('y',None)

output.createVariable('x','f4',('x',))
output.createVariable('y','f4',('y',))
output.createVariable('mask','f4',('y','x'))



output.variables['x'][:] = x
output.variables['y'][:] = y
print x.shape
print y.shape
print ascii_data.shape
print hdata
output.variables['mask'][:]= ascii_data

output.close()

print " To calculate the masked file use ncbo -op_typ=multiply your.nc mask.nc output.nc"
