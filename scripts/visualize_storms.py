from image_view import DynamicImshow
from smrf.envphys.storms import tracking
from netCDF4 import Dataset
import numpy as np

class StormViewer(DynamicImshow):
    def __init__(self,fname):
        super(StormViewer,variable_lst = ['prceip'] fname_lst = [fname])


    def f(self,i):
        """
        Modifier function for each image, in this case
        the data is simply stepped forward in time.
        """
        z = self.plot_num

        ds = self.ds[0]
        var = self.variable_lst[0]
        data = ds[var][i]

        if z==0:
            data = ds[var][i]
            self.plot_num+=1

        else:
            if storming:
                self.accum_precip += data

            else:
                self.accum_precip = np.zeros(ds[0].size)

            data = self.accum_precip
            self.plot_num = 0

        return data

if __name__ =='__main__':
    s = StormViewer()
