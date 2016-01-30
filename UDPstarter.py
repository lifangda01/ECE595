import subprocess
import os, sys

# TODO: read in topology table
numNodes = 3

cwd = os.getcwd()

subprocess.call(['gnome-terminal', '-x', 
				cwd + '/UDPserver.py'])

for i in range(1, numNodes+1):
	subprocess.call(['gnome-terminal', '-x', 
				cwd + '/UDPnode.py', str(i), 'localhost', '10000'])

