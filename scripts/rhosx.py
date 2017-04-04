#! /usr/bin/python
from math import exp
import pandas as pd
import argparse
import getpass

def ui():

    desc = """Estimates static new snow density (kg/m**3) from\n
            precipitation temperature (C) and mass (kg or mm m^2)\n"
            accounting for overburden (depth),\n"
            and temperature metamorphism compaction.\n"
            After Anderson (1976), Kojima (1967), Mellor (1964) & Yoshida (1963)\
            n"
            usage: rhosx Tpp pp """
    parser = argparse.ArgumentParser(description = desc)

    #parser.add_argument('-TP', dest='TP', type=float, help='temperature and precip total', required = False)

    parser.add_argument('-f','--file', dest='fname', help='filename containing Tpp and pp values', required = False)
    output_str =  "\nTpp\tpp\tswe\t%sno\trho-ns\tdrho-c\tdrho-m\trho-s\trho\tzs"
    print output_str
    args = parser.parse_args()
    temp = []
    precip = []
    response =""
    if args.fname ==None:
        while response != exit:
            response = getpass.getpass("")
            response = response.split()
            temp = float(response[0])
            precip = float(response[1])
            swe, pcs, rho_ns, d_rho_c, d_rho_m, rho_s, rho, zs = snow_rho(temp, precip)

            output_str = "%5.1f\t%5.1f\t%5.3f\t%5.2f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.2f\n"% (temp,precip, swe, pcs, rho_ns, d_rho_c, d_rho_m, rho_s, rho, zs)
            print output_str
    else:

        with open(args.fname) as f:
            data = f.readlines()
            for row in data:
                row = row.strip()
                row = row.split(' ')
                temp.append(float(row[0]))
                precip.append(float(row[1]))
            f.close()
    return temp, precip


def generate_density(temperature,overburden):
    """
    produce a pandas dataframe in holding all the density info
    """

    df = pd.DataFrame(columns = ('Total precip', 'Temp', 'swe', 'pcs', 'rho_ns', 'd_rho_c', 'd_rho_m', 'rho_s', 'rho', 'zs'))
    i = 0
    output_str =  "\nTpp\tpp\tswe\t%sno\trho-ns\tdrho-c\tdrho-m\trho-s\trho\tzs"
    print output_str
    sep_lst = len(output_str)
    print "-"*(sep_lst+30)

    for i in range(len(temperature)):

        swe, pcs, rho_ns, d_rho_c, d_rho_m, rho_s, rho, zs = snow_rho(temperature[i],overburden[i])
        df.loc[i] = [overburden[i], temperature[i], swe, pcs, rho_ns, d_rho_c, d_rho_m, rho_s, rho, zs]

        output_str = "%5.1f\t%5.1f\t%5.3f\t%5.2f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.2f\n"% (temperature[i], overburden[i], swe, pcs, rho_ns, d_rho_c, d_rho_m, rho_s, rho, zs)
        print output_str
        if i < len(temperature)-1  and temperature[i] != temperature[i+1]:
            print "="*(sep_lst+30)

    return df

def snow_rho(Tpp,pp):
    """
    New density model that takes into account the hourly temperature during precip
    and the total storm accumulated_precip.

    args:
    Tpp - a single value of the hourly temperature during the storm

    pp - a single value of the accumulated_precip precip during a storm


    returns:
    Tpp, pp, swe, pcs, rho_ns, d_rho_c, d_rho_m, rho_s, rho, zs

    Tpp - temperature during precip
    pp - precipitation accumulated
    swe - snow water equivalent
    pcs - percent snow
    rho_ns - density of new snow with out compaction
    d_rho_c -
    d_rho_m -
    rho_s - density of the snow with compaction
    rho - density of precip
    zs - snow height
    """
    ex_max = 1.75
    exr = 0.75
    ex_min = 1.0
    c1_min = 0.026
    c1_max = 0.069
    c1r = 0.043
    c_min = 0.0067
    cfac = 0.0013
    Tmin = -10.0
    Tmax = 0.0
    Tz = 0.0
    Tr0 = 0.5
    Pcr0 = 0.25
    Pc0 = 0.75

    water = 1000.0

    if pp >0.0:
        # set precipitation temperature, % snow, and SWE
        if Tpp < Tmin:
            Tpp = Tmin
            tsnow = Tmin

        else:
            if Tpp > Tmax:
                tsnow = Tmax
            else:
                tsnow = Tpp

        if Tpp <= -0.5:
            pcs = 1.0

        elif Tpp > -0.5 and Tpp <= 0.0:
            pcs = (((-Tpp) / Tr0) * Pcr0) + Pc0

        elif Tpp > 0.0 and Tpp <= (Tmax +1.0):
            pcs = (((-Tpp) / (Tmax + 1.0)) * Pc0) + Pc0

        else:
            pcs = 0.0

        swe = pp * pcs

        if swe > 0.0:
            # new snow density - no compaction
            Trange = Tmax - Tmin
            ex = ex_min + (((Trange + (tsnow - Tmax)) / Trange) * exr)

            if ex > ex_max:
                ex = ex_max

            rho_ns = (50.0 + (1.7 * (((Tpp - Tz) + 15.0)**ex))) / water

            # proportional total storm mass compaction
            d_rho_c = (0.026 * exp(-0.08 * (Tz - tsnow)) * swe * exp(-21.0 * rho_ns))

            if rho_ns * water < 100.0:
                c11 = 1.0
            else:
                #c11 = exp(-0.046 * ((rho_ns * water) - 100.0))
			    c11 = (c_min + ((Tz - tsnow) * cfac)) + 1.0

            d_rho_m = 0.01 * c11 * exp(-0.04 * (Tz - tsnow))

            # compute snow denstiy, depth & combined liquid and snow density
            rho_s = rho_ns +((d_rho_c + d_rho_m) * rho_ns)

            zs = swe / rho_s

            if swe < pp:
                if pcs > 0.0:
                    rho = (pcs * rho_s) + (1 - pcs)
                if rho > 1.0:
                    rho = water / water

            else:
                rho = rho_s

        else:
            rho_ns = 0.0
            d_rho_m = 0.0
            d_rho_c = 0.0
            zs = 0.0
            rho_s = 0.0
            rho = water / water

        # convert densities from proportions, to kg/m^3 or mm/m^2
        rho_ns *= water
        rho_s *= water
        rho *= water

    #No precip
    else:
        rho_ns = 0.0
        d_rho_m = 0.0
        d_rho_c = 0.0
        zs = 0.0
        rho_s = 0.0
        rho = 0.0
        swe = 0.0
        pcs = 0.0



    result = {'swe':swe, 'pcs':pcs,'rho_ns': rho_ns, 'd_rho_c' : d_rho_c, 'd_rho_m' : d_rho_m, 'rho_s' : rho_s, 'rho':rho, 'zs':zs}

    return result

if __name__ == '__main__':
    Tpp, pp = ui()
