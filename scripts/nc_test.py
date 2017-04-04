# import xarray as xr
#
# ds = xr.open_dataset('/home/micahjohnson/Desktop/test_output/wind_speed.nc',chunks={'time':1024})
from matplotlib import pyplot as plt
from netCDF4 import Dataset
from datetime import datetime
import time
import smrf
from smrf.envphys import snow
import numpy as np

time_step = 60.0

storms = [ {'start': datetime(2008,10,4,9),'end': datetime(2008,10,5,9)}]

pds = Dataset('/home/micahjohnson/Desktop/test_output/precip.nc','r')
dds = Dataset('/home/micahjohnson/Desktop/test_output/dew_point.nc','r')
storm_accum = np.zeros(pds.variables['precip'][0].shape)
#parse from file start time
sim_start = datetime.strptime((pds.variables['time'].units.split('since')[-1]).strip(),'%Y-%m-%d %H:%M:%S')
for i,storm in enumerate(storms):
    delta  = (storm['end']- storm['start'])
    storm_span = delta.total_seconds()/(60.0*time_step)
    print storm_span
    #reset the accumulated array
    storm_accum[:]= 0.0

    #convert to seconds from epoch
    seconds_start = (storm['start'] - sim_start).total_seconds()
    steps_start = int(seconds_start/(60.0*time_step))

    seconds_end = (storm['end'] - sim_start).total_seconds()
    steps_end = int(seconds_end/(60.0*time_step))

    steps = range(steps_start, steps_end)

    print "Processinfg storm #{0}".format(i)
    print "Accumulating precip..."
    for t in steps:
        storm_accum +=pds.variables['precip'][t][:][:]

    print "Calculating snow density..."
    for t in steps:
        start = time.time()
        dpt = dds.variables['dew_point'][t]
        snow_density = snow.compacted_density(storm_accum, dpt)
        #visual
        print "plotting timestep {0}".format(t)
        fig = plt.figure()
        a=fig.add_subplot(1,3,1)
        a.set_title('New Snow Density')

        plt.imshow(snow_density)
        plt.colorbar()

        b=fig.add_subplot(1,3,2)
        plt.imshow(dpt)
        plt.colorbar()
        b.set_title('Dew Point')

        c=fig.add_subplot(1,3,3)
        plt.imshow(storm_accum)
        c.set_title('Accum Precip in mm')
        plt.colorbar()

        print "Single time step took {0}s".format(time.time() - start)
        plt.show()

pds.close()
dds.close()
