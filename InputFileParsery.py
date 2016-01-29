import sys
import re

topology = []
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
