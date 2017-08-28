from rhosx import snow_rho, generate_density,ui

from matplotlib import pyplot as plt
from matplotlib import cm as cm
import numpy as np

import pandas as pd


def plot_multi_series(nplots_col_name,x_col_name, y_col_name,df):
    """
    Designed for handling multiple lines to one graph using pandas df.
    Ultimately this is nice for handling multidimensional data that can be
    visualized using 2D. Such that we are interested in :

     y_col_name = f(x_col_name,nplots_col_name), plot ---> rho f(nplots_col_name=const, x_col_name)

     E.g. rho = f(Precip, Temp) -----> plot rho = f(Precip = const, Temp)

    args:
    nplots_col_name - the column name you would like to make multiple graphs of

    x_col_name - x axis column name

    y_col_name - y axis column name
    """

    fig = plt.figure(figsize=(11,11))
    ax = plt.subplot(111)
    for i in df[nplots_col_name].unique():
        burden_cat = df[nplots_col_name] == i
        plot_data = df[burden_cat]

        ax.plot(plot_data[x_col_name],plot_data[y_col_name],label='{0} = {1}'.format(nplots_col_name,i))
        # Put a legend below current axis

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12),
              fancybox=True, shadow=True, ncol=5)

    return ax

def plot_multi_dim_surf(x_col_name, y_col_name, z_col_name, df):
    """
    Designed for plotting multidimensional data to one plot using pandas df.


    z_col_name = f(x_col_name,y_col_name), plot ---> z f(x_col_name=const, y_col_name)

    E.g. rho = f(Precip, Temp) -----> plot rho = f(precip Temp)

    args:
    x_col_name - x axis column name

    y_col_name - y axis column name

    z_column_name - surf values to plot on an xy grid
    """
    ax = plt.subplot(111)
    ax.imshow(df[x_col_name], df[y_col_name], df[z_col_name])
    return ax

def plot_all_density_domain(tmin = -12, tmax = 2, precip_min = 0, precip_max = 500):

        t_delta = 0.01

        pp_delta = 10

        plot_rows = 2
        plot_columns = 4

        levels_dict = {'swe':[],
                    'pcs':[],
                    'rho_ns': np.arange(0,250,50),
                    'd_rho_c' : [],
                    'd_rho_m' : [],
                    'rho_s' : np.arange(0,350,50),
                    'rho':[100,200,400,800],
                     'zs':np.arange(0,3000,500)}

        titles_dict = {'swe':'SWE',
                    'pcs':'% Snow',
                    'rho_ns': "Fresh Snow Density (No Compaction)",
                    'd_rho_c' : "Density Compaction Factor",
                    'd_rho_m' : "Density Metamorphism Factor",
                    'rho_s' : "Snow Density after Compaction",
                    'rho': "Final Density of Precip.",
                     'zs':"Snow Height [mm]"}

        contour_levels = np.arange(0,1,0.05)

        #Create input/output arrays and generate  a mesh
        T_range = np.arange(tmin,tmax,t_delta)
        PP_range = np.arange(precip_min,precip_max,pp_delta)
        T,PP = np.meshgrid(PP_range,T_range)

        #Get the dictionary from the point model
        params = snow_rho(-1,10)

        plot_data_dict = {}
        for k in params.keys():
            plot_data_dict[k] = np.zeros(T.shape)

        #Calculate density
        for i,t in enumerate(T_range):
            for j,p in enumerate(PP_range):
                params = snow_rho(t,p)
                for k,v in params.items():
                    plot_data_dict[k][i][j] = v

        num_plots = len(plot_data_dict.keys())
        # row and column sharing
        f, axarray = plt.subplots(plot_rows,plot_columns, sharex='col', sharey='row')

        i = 0
        j = 0
        for k,v in plot_data_dict.items():

            ax = axarray[i][j]

            plot_extent = [T.min(), T.max(), PP.min(), PP.max()]
            im = ax.imshow(v, extent = plot_extent,
            interpolation='nearest', origin='lower',aspect='auto')
            f.colorbar(im, ax = ax)

            #Throw some contours on it.
            if len(levels_dict[k]) > 0:
                CS = ax.contour(v,levels_dict[k],colors='k', extent = plot_extent)
                ax.clabel(CS,inline=1,inline_spacing=-5,fontsize=10,fmt='%1.0f',colors='k')

            #Label this bad boy
            ax.set_ylabel('Temperature [C]')
            ax.set_xlabel('Storm Precip Total [mm]')
            ax.set_title(titles_dict[k])

            if i < len(axarray):
                if j < len(axarray[:][0])-1:
                    j+=1
                else:
                    i+=1
                    j = 0

        plt.show()

if __name__ == '__main__':
    plot_all_density_domain()
