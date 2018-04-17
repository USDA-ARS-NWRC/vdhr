#!/usr/bin/env python
from matplotlib import pyplot as plt

import pandas as pd

import argparse 

def time_series(csv_name):
	df = pd.read_csv(csv_name)
	df['ATLI1'].plot.line()
	plt.show()
def main():
	parser = argparse.ArgumentParser(description='Visualize some station data')
	parser.add_argument('filename', metavar='f', type=str,
                    help='filename pointing to station date csv file')
	args = parser.parse_args()	
	time_series(args.filename)

if __name__ == '__main__':
	main()
