import ncEarth
import matplotlib
# import argeparse
import sys



def make_movie_over_lay(fname, variables):
    """
    Write out images for time series overlay for Google Earth.
    Args:
        fname - Path to NetCDF
        variables -list of strings naming variables to output
    """
    kmz=ncEarth.ncNWRC_mov(fname)
    kmz.write('thickness','output.kmz')


if __name__ == '__main__':
    print(sys.argv)
    variables = sys.argv[2].split(',')
    print(variables)
    make_movie_over_lay(sys.argv[1],variables)
