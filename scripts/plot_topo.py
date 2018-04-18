from netCDF4 import Dataset
import matplotlib.pyplot as plt
import sys
import numpy as np

d = Dataset(sys.argv[1])

plot_data = d.variables[sys.argv[2]][:]
if len(plot_data.shape) == 2:
	plt.imshow(plot_data)
else:
	plt.plot(plot_data)
plt.show()
