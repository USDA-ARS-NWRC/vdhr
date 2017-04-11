from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class animate_image():
    def __init__(self,filename, variable):
        fig = plt.figure()
        self.variable = variable

        self.ds = Dataset(filename,'r')

        self.current_step = 0
        self.ims = []
        self.steps = self.parse_steps()
        print self.steps
        #Create data plot
        self.ims = self.update_fig()

        #plot the rest to an animator
        ani = animation.ArtistAnimation(fig, self.ims, interval = 0,repeat_delay = 1000,  blit=True)
        plt.show()

    def parse_steps(self):
        """
        Determines the total number of time steps available
        """

        return self.ds.dimensions['time'].size



    def update_fig(self):
        """
        cycles through each time step and plots the data to the animator
        """
        for i in range(self.steps):
            im = plt.imshow(self.ds.variables[self.variable][self.current_step], animated=True)
            self.ims.append([im])
        return self.ims


if __name__ == '__main__':
    ani = animate_image('/home/micahjohnson/Desktop/test_output/precip.nc', 'precip')
