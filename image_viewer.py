from netCDF4 import Dataset
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class DynamicImage():
    def __init__(self,filename,variable, ax = None, fig = None, data_modifier = None,start_step = 0, end_step = None):
        """
        Instantiating the image viewer class will automatically create the animator.
        User is still required to add plt.show() somewhere to get the desired image

        Args:
            filename - path to the 2D  NetCDF image
            variable - variable name inside the Netcdf file to read.
            start_step - Where to start the animation, Default is the beginning
            end_step - Where to end the animation, default is none, when value is none
                        step is set to the final step.
        Returns:
            matplotlib.animation.ArtistAnimation
        """
        #Allow user to pass in figs
        if ax == None:
            ax = plt

        if fig == None:
            fig = plt.figure()
            print "\nERROR you still dont know what to do here"
        self.ax = ax
        self.fig = fig
        self.variable = variable

        #Open the netCDF dataset
        self.ds = Dataset(filename,'r')

        self.steps = self.parse_steps()

        #Set the start and stops supplied by user
        self.start = start_step
        self.end = end_step

        #Was an end step supplied?
        if self.end == None:
            self.end = self.steps

        #Create data plot
        self.ims = self.update_fig(modifier_func = data_modifier)

        print "\nCreating animation using file {0} and variable {1}".format(filename,variable)
        print "Total number for time steps available: {0}".format(self.steps)
        print "Total number for time steps animated: {0}".format(self.end - self.start)


    def parse_steps(self):
        """
        Determines the total number of time steps available

        Args:
            None

        Returns:
            Integer of the number of timesteps in the file
        """

        return self.ds.dimensions['time'].size

    def update_fig(self,modifier_func):
        """
        Cycles through each time step and collects the matplotlib image objects created
        when using imshow, these are appended to a list and returned.

        Args:
            modifier_func - This is a user defined function that would recieve
                            a single time step of the image data, operate on it
                            and return the data this function.
        Returns:
            self.ims - a list of matplotlib.image.AxesImage objects the represent
                        each timestep.
        """
        ims = []
        for i in range(self.start, self.end):

            data = self.ds.variables[self.variable][i]

            #Apply a data modification if any supplied
            if modifier_func != None:
                data = modifier_func(data)
            im = self.ax.imshow(data, animated=True,aspect='auto')
            ims.append([im])
        self.ims = ims
        return self.ims

    def finalize(self):
        #plot the rest to an animator
        self.ds.close()
        return  animation.ArtistAnimation(self.fig, self.ims, interval = 50,repeat_delay = 1500,  blit=True)

class CompareDynamicImages(DynamicImage):
    def __init__(self, image_lst,variable_lst,data_modifier_lst = None):
        
        if data_modifier_lst == None:
            data_modifier_lst = []
            for i in range(len(image_lst)):
                data_modifier_lst.append(None)

        #Check for validity
        for i,f in enumerate(image_lst):
            if not os.path.isfile(f):
                image_lst.pop()
                variable_lst.pop()
                data_modifier_lst.pop()

                print "WARNING: {0} does not exist, removing from list.".format(f)

        self.num_plots = len(image_lst)
        print "Number of plots: {0}".format(self.num_plots)

        #Only 1 row until we reach 3
        if self.num_plots < 4:
            num_rows = 1
            num_cols = self.num_plots

        #Odd number generate 2 X (num_plots+1)/2 e.g.
        # XXXXX
        # XXXX
        elif self.num_plots % 2 != 0:
            num_cols = (self.num_plots+1) % 2
            num_rows = 2
        #Even number 2 rows of num_plots/2
        else:
            num_cols = self.num_plots/2
            num_rows = 2
        print "Plotting the figures in a {0} rows by {1} columns matrix".format(num_rows,num_cols)
        f, axarray = plt.subplots(num_rows,num_cols, sharex='col', sharey='row',squeeze = False)

        i = 0
        j = 0
        self.animations = []
        for z,fname in enumerate(image_lst):

            ax = axarray[i][j]
            try:
                self.animations.append(DynamicImage(fname,variable_lst[z],ax = ax,fig = f,start_step=0, end_step = 10, data_modifier = data_modifier_lst[z]))
            except Exception as e:
                print "\nERROR: In file {0} while attempting to grab time step #{1} for variable {2}".format(fname,z,variable_lst[z])
                print e
            if i < range(num_rows):
                if j < range(num_cols):
                    j+=1
                else:
                    i+=1
                    j = 0

    def finalize(self):
        for ani in self.animations:
            ani.finalize()

if __name__ == '__main__':
    ani = DynamicImage('/home/micahjohnson/Desktop/test_data/precip.nc', 'precip')
    f = ani.finalize()

    # precip_lst = [
    # '/home/micahjohnson/Desktop/test_data/precip.nc',
    # '/home/micahjohnson/Desktop/test_data/thermal.nc'
    # ]
    # var_lst =[
    #     'precip',
    #     'thermal'
    # ]
    # ani = CompareDynamicImages(precip_lst,var_lst)
    # ani.finalize()
    plt.show()
