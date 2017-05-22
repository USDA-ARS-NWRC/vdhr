import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from netCDF4 import Dataset
import os


class DynamicImshow():
    def __init__(self,variable_lst,ds_lst = None, fname_lst = None):
        self.ds = []
        self.ims = []
        self.variable_lst =[]
        self.modifier = {}
        self.i = 0
        self.plot_num = 0

        #Allow the user to specify whether to instantiate data from file or bring their own data
        if ds_lst == None and type(fname_lst)==list:
            #Check for filenames
            for i,fname in enumerate(fname_lst):
                if os.path.isfile(fname):
                    self.ds.append(Dataset(fname,'r'))
                    self.variable_lst.append(variable_lst[i])
                else:
                    print "Error: File does not exitst \n {0}".format(fname)

        elif fname_lst == None and type(ds_lst)==list:
            self.ds = ds_lst

        else:
            raise ValueError("User must provide either ds_lst or fnames_lst for data.")

        #Check user inputs
        if len(self.variable_lst) != len(self.ds):
            raise ValueError("User must provide the same number of variable names as datasets.")

    def animate(self):
        """
        Produce the animation
        """

        #TO-DO to be updated to manage multiple rows
        fig, axarray = plt.subplots(1, len(self.ds), sharex='col', sharey='row')

        #Create a surface plot of each timestep starting here, intiialized below.
        for j,ax in enumerate(axarray):
            ax.set_aspect('equal', 'datalim')
            ax.set_adjustable('box-forced')
            im = ax.imshow(self.f(self.i), cmap=plt.get_cmap('viridis'), animated=True)
            fig.colorbar(im,ax=ax)
            self.ims.append(im)

        #Update each plot and create a animation to show
        ani = animation.FuncAnimation(fig, self.updatefig, interval=1000, blit=True)
        plt.show()
        self.close()


    def f(self,i):
        """
        Modifier function for each image, in this case
        the data is simply stepped forward in time.
        """
        z = self.plot_num
        ds = self.ds[z]
        var = self.variable_lst[z]
        if self.plot_num<len(self.ds)-1:
            self.plot_num+=1
        else:
            self.plot_num = 0

        return ds[var][i]


    def updatefig(self,*args):
        """
        Called by the animator function to update the images
        """
        self.i+=1

        if self.i > 3000:
            self.i = 0
        for j in range(len(self.ims)):
            self.ims[j].set_array(self.f(self.i))
        return self.ims

    def close(self):
        for ds in self.ds:
            ds.close()



if __name__ == "__main__":
    fnames = ["../smrf_runs/full_output/precip.nc",
	      "../smrf_runs/full_output/snow_density.nc"]
    vars_lst = ['precip','snow_density']

    t = DynamicImshow(vars_lst, fname_lst = fnames)
    t.animate()
