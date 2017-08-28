from smrf.envphys.snow import calc_phase_and_density,susong1999,piecewise_susong1999,marks2017
from matplotlib import pyplot as plt
import numpy as np
from numpy.linalg import lstsq
from sympy import Symbol, pprint,expand, evalf

def generate_equation(coefficients,order = 2):
    T = Symbol('y')
    PP = Symbol('x')
    final = 0
    T_terms = []
    PP_terms = []
    term = []

    j = 0
    for i in range(order+1):
        T_terms.append(T**i)
        PP_terms.append(PP**i)

    for x in T_terms:
        for y in PP_terms:
            term.append(coefficients[j]*x*y)
            j+=1
    for t in term:
        final += t

    pprint(final)
    return final

def curve_fit(PP,T,rho, order = 1):

    print "Calculating fit for data of order {0}...".format(order)
    #Generate the inputs
    PP = PP.flatten()
    T = T.flatten()
    X = []
    Y = []
    terms = []
    #Create 2 lists of type 1,x,x**2,x**3...
    for i in range(order+1):
        X.append(PP**i)
        Y.append(T**i)

    #Generate a list of generic poly terms i.e.
    # [1,x,y,xy,x**2y, x*y**2,x**2,y**2]
    for x in X:
        for y in Y:
            terms.append(x*y)

    A = np.array(terms).T
    B = rho.flatten()
    print A.shape
    print B.shape

    coef,residual,rank,minimum = lstsq(A,B)

    return coef,residual


def plot_compare_curve_fit(PP,T,model_name,curve):
        models = [model_name,"curve_fit","residual"]
        fig, axarray = plt.subplots(1,len(models), sharex='col', sharey='row')

        for  z,f in enumerate(models):
            ax = axarray[z]
            if f == model_name:
                density,perc_snow = calc_phase_and_density(T,PP,nasde_model = f)
                density_1 = density
            elif f=="curve_fit":
                density = np.zeros(T.shape)

                for (i,j),t in np.ndenumerate(T):
                    y = t
                    x = PP[i][j]
                    density[i][j] = curve.evalf()
                density_2 = density
                plot_snow_model(PP,T,density,ax)

            else:
                residual = abs(density_2- density_1)
                pc = ax.pcolormesh(PP,T,residual)

def plot_snow_model(PP,T,rho,ax):
    plot_extent = [PP.min(), PP.max(), T.min(), T.max()]

    pc = ax.pcolormesh(PP,T,density)

    CS = ax.contour(PP,T,density, [75,100,150,200,250], colors='k', interpolaton = 'none')

    ax.clabel(CS, inline=1, inline_spacing=-5, fontsize=12, fmt='%1.0f', colors='k')

    #Label this bad boy
    ax.set_ylabel('Temperature [C]')
    ax.set_xlabel('Storm Precip Total [mm]')
    ax.set_title(f)


def plot_all_models(T,P):
    models = ["susong1999","piecewise_susong1999","marks2017"]
    fig, axarray = plt.subplots(1,len(models), sharex='col', sharey='row')

    for  z,f in enumerate(models):
        ax = axarray[z]
        density,perc_snow = calc_phase_and_density(T,PP,nasde_model = f)
        plot_snow_model(PP,T,density,ax)
    plt.show()

def main():
    tmax = 5
    tmin = -15
    pmax = 1000
    pmin = 0
    t_delta = 0.01
    pp_delta = 1

    model = 'marks2017'

    #Create input/output arrays and generate  a mesh
    T_range = np.arange(tmin,tmax,t_delta)
    PP_range = np.arange(pmin,pmax,pp_delta)
    PP,T = np.meshgrid(PP_range,T_range)
    order = 2
    density,perc_snow = calc_phase_and_density(T,PP,nasde_model = model)
    coef,residual = curve_fit(PP,T,density,order = order)
    print "Coefficients: {0}".format(coef)
    print "Residual = {0}".format(residual)

    equation = generate_equation(coef,order = order)
    plot_compare_curve_fit(PP,T,model,equation)
    #plot_snow_model(PP,T)

if __name__ == '__main__':
    main()
