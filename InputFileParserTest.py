import sys
import re
import settings

with open(settings.fileName, 'r') as inputFile:
	number_switches = inputFile.readline()
	for line in inputFile:
		settings.topology.append(line.strip().split(' '))

if __name__ == "__main__":
	print (" ")
	print ("The number of switches in the topology = " + number_switches)
	for item in settings.topology:
		print (item)
	print (" ")
