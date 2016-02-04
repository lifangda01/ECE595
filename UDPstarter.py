import subprocess
import os, sys
import argparse
from InputFileParser import number_switches

parser = argparse.ArgumentParser(description='Create a centralized UDP network.')

# Required arguments
parser.add_argument('topoFile', metavar='filename',
					help="Name of the topology file")

# Optional arguments
parser.add_argument('-v', action='store_true', default=False,
					help="Enable high verbosity")

args = parser.parse_args()

cwd = os.getcwd()

# topology, number_switches = readInputFile(args.topoFile)
# subprocess.call(['python', cwd + '/InputFileParser.py', args.topoFile])

# Read in topology table
numNodes = int(number_switches)


argList = ['gnome-terminal', '-x', 
			cwd + '/UDPserver.py', 'localhost', '10000']
if args.v:
	argList.append('-v')

subprocess.call(argList)

for i in range(1, numNodes+1):
	argList = ['gnome-terminal', '-x', 
				cwd + '/UDPnode.py', str(i), 'localhost', '10000']
	if args.v:
		argList.append('-v')
	subprocess.call(argList)

