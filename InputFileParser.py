import sys
import re
import argparse

# parser = argparse.ArgumentParser(description='Parse a topology file')

# # Required arguments
# parser.add_argument('topoFile', metavar='filename',
# 					help="Name of the topology file")

# args = parser.parse_args()

topology = []
number_switches = 0
with open('SampleInputFile1.txt', 'r') as inputFile:
	number_switches = inputFile.readline()
	for line in inputFile:
		topology.append(line.strip().split(' '))

if __name__ == "__main__":
	print (" ")
	print ("The number of switches in the topology = " + number_switches)
	for item in topology:
		print (item)
	print (" ")
