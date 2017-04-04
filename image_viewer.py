from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation



class animate_image():
    def __init__(self,fname, variable):
        fig = plt.figure()
        self.variable = variable

        self.ds = Dataset(fname,'r')

        self.current_step = 0
        self.steps = self.parse_steps()

        #Create initil plot
        self.im = plt.imshow(self.ds.variables[self.variable][self.current_step], animated=True)

        #plot the rest to an animator
        ani = animation.FuncAnimation(fig, self.update_fig, interval=50, blit=True)
        self.ds.close()
        plt.show()

    def parse_steps(self):
        """
        Determines the total number of time steps available
        """

        return self.ds.dimensions['time'].size


    def update_fig(self,*args):
        """
        cycles through each time step and plots the data to the animator
        """

        if self.current_step < self.steps:
            self.current_step+=1

        self.im.set_array(self.ds.variables[self.variable][self.current_step])
        return self.im,


if __name__ == '__main__':
    ani = animate_image('/home/micahjohnson/Desktop/test_output/precip.nc', 'precip')
