from netCDF4 import Dataset
import numpy as np
import argparse
import os

#Convert an ascii file to netcdf
parser = argparse.ArgumentParser()

parser.add_argument("mask", type=str,
                    help="Full filename for mask netcdf file.")
parser.add_argument("unmasked_var", type=str,
                    help="Full filename for netcdf file to mask.")


parser.add_argument("variable", type=str,
                    help="variable name in unmasked_var.nc")


parser.add_argument("-o","--output", type=str,
                    help="""output file. If none is provided, the
                    filename is the same as the ascii file but in current directory and
                    with the netcdf file extension.""",
                    default=None)


args = parser.parse_args()
unmasked = Dataset(args.unmasked_var,'r')
variable_name = args.variable
mask = Dataset(args.mask)

#Parse the option name
if args.output is None:
    #Isolate the name of the input file and use it for netcdf
    out_fname = "masked_"+(os.path.split(args.unmasked_var)[-1]).split('.')[0]+'.nc'
else:
    out_fname = args.output

print "writing masked result to {0}".format(out_fname)
output = Dataset("."+os.sep+out_fname,'w')


for name, dimension in unmasked.dimensions.iteritems():
    output.createDimension(name, len(dimension) if not dimension.isunlimited() else None)

for name, variable in unmasked.variables.iteritems():

    var = output.createVariable(name, variable.datatype, variable.dimensions)
    print name
    # take out the variable you don't want
    if name != variable_name:
        output.variables[name][:] = unmasked.variables[name][:]

for t in unmasked.variables['time'][:]:
    output.variables[variable_name][t,:,:]= unmasked.variables[variable_name][t,:,:]*mask.variables['mask'][:]

output.close()
