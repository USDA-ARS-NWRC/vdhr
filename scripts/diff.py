###########################
#
# Usage: Difference
#
#
###########################

import sys
import os
from netCDF4 import Dataset
import argparse
import numpy as np
import progressbar
import datetime as dt

class NCDiffer(object):
    def __init__(self, fname_orig, fname_new, var_orig=None, var_new=None,
                            var_new_time_shift=None, var_orig_time_shift=None):
        """
        A smart differencing tool for comparing netcdf output

        Args:
            fname_orig: Filename of the original file thats considered the basis for
                        comparison
            fname_new: fileaname of the netcdf being compared
            var_orig: variable name in the original netcdf file
            var_new: variable name in the new netcdf file
            var_new_time_shift: shifts the comparison file in time for comparing files
                                different starting points
            var_orig_time_shift: shifts the original file in time for comparing files
                                different starting points
        """
        self.fname_orig = os.path.abspath(fname_orig)
        self.fname_new = os.path.abspath(fname_new)

        self.orig = Dataset(self.fname_orig)
        self.new = Dataset(self.fname_new)

        #Seach for var names
        if var_new == None:
            for v in self.new.variables:
                if v.lower() not in ['time','x','y']:
                    self.var_new = v

        else:
            self.var_new = var_new

        # No variable found, attempt to find a suitable one
        if var_orig == None:
            for v in self.orig.variables:
                if v.lower() not in ['time','x','y']:
                    self.var_orig = v

        else:
            self.var_orig = var_orig

        # Comparison file time shift requested
        orig_start = 0
        new_start = 0

        is_timeshifted = False

        # New file timeshift requested
        if var_new_time_shift != None and var_orig_time_shift == None:
            print("Warning: time shifting being used on comparison file")
            new_start = var_new_time_shift
            is_timeshifted = True
            shift = var_new_time_shift

        # Original file timeshift requested
        elif var_new_time_shift == None and var_orig_time_shift != None:
            print("Warning: time shifting being used on comparison file")
            is_timeshifted=True
            orig_start = var_orig_time_shift
            shift = var_orig_time_shift

        # Both requests, creates and error
        elif var_new_time_shift != None and var_orig_time_shift != None:
            print("ERROR: Please only specify a single timeshift.")
            sys.exit()

        # Use only positive whole numbers to simplify
        if is_timeshifted:
            try:
                v = int(shift)

            except:
                print("Please use a whole integers for time shifts")
                sys.exit()

            if not v > 0.1:
                print("Please use a whole positive integer for time shifts")
                sys.exit()


        # Check for timesteps mismatching

        try:
            self.time_data_orig = self.orig.variables['time'][orig_start:-1]
        except:
            print("No time variable provided for {}".format(self.fname_orig))
            try:
                self.time_data_orig = self.orig.variables['Time'][orig_start:-1]
            except:
                self.time_data_orig = np.arange(orig_start,len(self.orig.dimensions['Time'])-1)

        self.timesteps_o = len(self.time_data_orig)


        self.time_data_new = self.new.variables['time'][new_start:-1]
        self.timesteps_n = len(self.time_data_new)

        self.timesteps = min([self.timesteps_n,self.timesteps_o])

        msg = ("\nWarning: Not using the full time period due to mismatch.\n"
              "Defaulting to time period for the {0} file ({1})")


        # Determine which timesteps are smaller and use that for calculating
        if self.timesteps_n > self.timesteps_o:
            fname = "original"
            f = self.fname_orig
            obj_to_copy = self.orig
            self.var_to_copy = self.var_orig

        elif self.timesteps_n < self.timesteps_o:
            fname = "new"
            f = self.fname_new
            obj_to_copy = self.new
            self.var_to_copy = self.var_new


        # Inform the user
        if self.timesteps_o==self.timesteps_n:
            msg = "\nTime periods are matched in length, using full time period."
            print(msg)
        else:
            print(msg.format(fname,self.timesteps))
            print("\nFile with smaller time range:\n{0}".format(f))

        # Build a description of the output
        self.description = ""
        print("\nDifferencing Details:"
              "\n======================")
        self.description+=("* Comparator: "
              "\n\t- File: {0}"
              "\n\t- Variable Name: {1}").format(self.fname_new,
                                             self.var_new)
        # Add print statement
        if var_new_time_shift != None:
            self.description+=("\n\t- timeshifted by: {0}".format(var_new_time_shift))

        # Add print statement
        self.description+=("\n* Basis:"
              "\n\t- File: {0}"
              "\n\t- Variable Name: {1}").format(self.fname_orig,
                                             self.var_orig)
        if var_orig_time_shift != None:
            self.description+=("\n\t- timeshifted by: {0}".format(var_orig_time_shift))

        self.description+=("\n* Total Timesteps: {0}").format(self.timesteps)
        print(self.description)

        self.create_output(obj_to_copy)

    def diff(self, time_enumerator):
        """
        subtracts the two images at a single timestep, the time timestep is
        determined by the user whether a shift is requested.
        """
        #print(int(self.time_data_new[time_enumerator]),
        #     int(self.time_data_orig[time_enumerator]))
        self.result = self.new.variables[self.var_new][self.time_data_new[time_enumerator]][:]\
                     - self.orig.variables[self.var_orig][self.time_data_orig[time_enumerator]][:]

    def create_output(self,obj_to_copy,f_out='./out.nc'):
        """
        Creates the output for the difference image.
        """

        print("\nCreating output file...")
        self.out = Dataset(f_out,mode = 'w',format='NETCDF4')
        #print("\nAdding dimensions to {0}...".format(f_out))

        self.out.description = self.description

        self.out.history ="Created {0}".format(
                                (dt.datetime.now().strftime("%y-%m-%d %H:%M")))

        for d,dimension in obj_to_copy.dimensions.items():
            self.out.createDimension(d,(len(dimension) if not dimension.isunlimited() else None))

        print("\nAdding variables to {0}...".format(f_out))

        for name,var in obj_to_copy.variables.items():
            print("\t{0}".format(name))
            self.out.createVariable(name, var.datatype, var.dimensions)
            if name.lower() in ['time','x','y']:
                self.out[name][:] = obj_to_copy.variables[name][:]

    def output(self,timestep,f_out='./out.nc'):
        self.out.variables[self.var_to_copy][timestep] = self.result

    def close(self):
        self.out.close()
        self.orig.close()
        self.new.close()

def main():
    print("\n=========== Smart NC Diff v0.1.0 ==========")
    parser = argparse.ArgumentParser(description='Provide a comparison on Netcdf files.')
    parser.add_argument('new_file', metavar='N', type=str,
                    help='Netcdf file to be compared.')
    parser.add_argument('orig_file', metavar='F', type=str,
                    help='Netcdf file to be compared against.')

    parser.add_argument('--var_orig','-vo', metavar='vo', type=str, default=None,
                    help='Netcdf variable name to be compared against.')
    parser.add_argument('--var_new','-vn', metavar='vn', type=str, default=None,
                    help='Netcdf variable name to be compared.')
    parser.add_argument('--new_time_shift','-nt', metavar='nt', type=int, default=None,
                    help='Compare the new file by shifting the time (e.g. var_n[dt+shift] - var2[dt]).')
    parser.add_argument('--orig_time_shift','-ot', metavar='ot', type=int, default=None,
                    help='Compare against the old file by shifting the time (e.g. var_n[dt] - var2[dt+shift]).')
    args = parser.parse_args()

    differ = NCDiffer(args.orig_file, args.new_file, var_orig=args.var_orig,
                                                     var_new=args.var_new,
                                                     var_orig_time_shift=args.orig_time_shift,
                                                     var_new_time_shift=args.new_time_shift)

    bar = progressbar.ProgressBar(max_value=differ.timesteps)

    for i in range(differ.timesteps):
        differ.diff(i)
        differ.output(i)
        bar.update(i)

    differ.close()

if __name__ == '__main__':
    main()
