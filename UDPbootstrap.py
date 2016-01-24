import subprocess
import sys

# Setup host
subprocess.call(['python UDPserver.py &'], shell=True)

# Setup switches
subprocess.call(['python UDPnode.py 1 localhost 10000 &'], shell=True)
subprocess.call(['python UDPnode.py 2 localhost 10000 &'], shell=True)

# subprocess.call(['ls','-l'])
