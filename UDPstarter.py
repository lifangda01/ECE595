import subprocess
import os, sys
import argparse

parser = argparse.ArgumentParser(description='Create a centralized UDP network.')

# Required arguments
parser.add_argument('topoFile', metavar='filename',
					help="Name of the topology file")

# Optional arguments
parser.add_argument('-v', action='store_true', default=False,
					help="Enable high verbosity")

args = parser.parse_args()

cwd = os.getcwd()

# Read in topology table
with open(args.topoFile, 'r') as inputFile:
	number_switches = inputFile.readline()
numNodes = int(number_switches)

argList = ['gnome-terminal', '-x', 
			cwd + '/UDPserver.py', 'localhost', '10000', args.topoFile]
if args.v:
	argList.append('-v')

subprocess.call(argList)

for i in range(1, numNodes+1):
	argList = ['gnome-terminal', '-x', 
				cwd + '/UDPnode.py', str(i), 'localhost', '10000']
	if args.v:
		argList.append('-v')
	subprocess.call(argList)
