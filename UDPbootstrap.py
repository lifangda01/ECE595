import subprocess

# Setup host
subprocess.call(['python UDPserver.py &'], shell=True)

# Setup switches
subprocess.call(['python UDPnode.py &'], shell=True)
subprocess.call(['python UDPnode.py &'], shell=True)

# subprocess.call(['ls','-l'])
