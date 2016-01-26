import subprocess
import os, sys

cwd = os.getcwd()

subprocess.call(['gnome-terminal', '-x', 
				cwd + '/UDPserver.py'])

subprocess.call(['gnome-terminal', '-x', 
				cwd + '/UDPnode.py', '1', 'localhost', '10000'])

subprocess.call(['gnome-terminal', '-x', 
				cwd + '/UDPnode.py', '2', 'localhost', '10000'])

