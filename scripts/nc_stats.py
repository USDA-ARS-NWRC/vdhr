from netCDF4 import Dataset
import numpy as np
import progressbar as pb


#Open data set
filename = '/home/micahjohnson/Desktop/test_output/precip.nc'
ds = Dataset(filename, 'r')
f = ds.variables['precip']

#collect important info create arrays
nt,nx,ny = np.shape(f)
maxes = []
mins = []
means = []

print "Processing netCDF statistics..."

#Create a progress bar to info the user
bar = pb.ProgressBar(max_value=nt)

#Iterate through all the timesteps and gather info.
for i in range(nt):
    img = f[i,:,:]
    maxes.append(np.max(img))
    mins.append(np.min(img))
    means.append(np.average(img))
    bar.update(i)

ds.close()

#Output to screen
print "="*100
print " "*3 + "NetCDF statistics" + " "*3
print "="*100
print ""
print "Filename: {0}".format(filename)
print "All time maximum: {0}".format(max(maxes))
print "All time minimum: {0}".format(min(mins))
print "All time average: {0}".format(np.average(means))
