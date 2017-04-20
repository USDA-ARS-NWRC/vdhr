import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from netCDF4 import Dataset
import os


class DynamicImshow():
    def __init__(self,fname_lst,variable_lst):
        self.ds = []
        self.ims = []
        self.variable_lst =[]
        self.i = 0
        self.plot_num = 0
        for i,fname in enumerate(fname_lst):
            if os.path.isfile(fname):
                self.ds.append(Dataset(fname,'r'))
                self.variable_lst.append(variable_lst[i])
            else:
                print "Error: File does not exitst \n {0}".format(fname)


        fig, axarray= plt.subplots(1, 3, sharex='col', sharey='row')
        # ax1.set_aspect('equal', 'datalim')
        # ax1.set_adjustable('box-forced')
        # ax2.set_aspect('equal', 'datalim')
        # ax2.set_adjustable('box-forced')
        # ax3.set_aspect('equal', 'datalim')
        # ax3.set_adjustable('box-forced')



        #You need to specify which ax object is getting which data and colormap
        for j,ax in enumerate(axarray):
            self.ims.append(ax.imshow(self.f(self.i), cmap=plt.get_cmap('viridis'), animated=True))
        #fig.colorbar(im1,ax=ax1)
        #
        # im2 = ax2.imshow(g(i), cmap=plt.get_cmap('viridis'), animated=True)
        # #fig.colorbar(im2,ax=ax2)
        #
        # im3 = ax3.imshow(h(i), cmap=plt.get_cmap('viridis'), animated=True)

        ani = animation.FuncAnimation(fig, self.updatefig, interval=50, blit=True)
        plt.show()

    def f(self,i):
        z = self.plot_num
        ds = self.ds[z]
        var = self.variable_lst[z]

        if self.plot_num<len(self.ds)-1:
            self.plot_num+=1
        else:
            self.plot_num = 0

        return ds[var][i]

    #fig.colorbar(im3,ax=ax3)

    def updatefig(self,*args):
        self.i+=1

        if self.i > 10:
            self.i = 0
        for j in range(len(self.ims)):
            self.ims[j].set_array(self.f(self.i))
        return self.ims


if __name__ == "__main__":
    fnames = ["/home/micahjohnson/Desktop/test_output/precip.nc",
              "/home/micahjohnson/Desktop/test_output/air_temp.nc",
              "/home/micahjohnson/Desktop/test_output/dew_point.nc"]
    vars_lst = ['precip','air_temp','dew_point']

    t = DynamicImshow(fnames,vars_lst)
