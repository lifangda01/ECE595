import subprocess
import os, sys, fcntl
import time

# Setup host
server = subprocess.Popen(['./UDPserver.py'], 
# server = subprocess.Popen(['python -u UDPserver.py &'], 
				shell=True, 
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
# Make read non-blocking, raise an IOError if msg is empty
fcntl.fcntl(server.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

# Setup switches
switches = []
s = subprocess.Popen(['./UDPnode.py 1 localhost 10000'], 
# s = subprocess.Popen(['python -u UDPnode.py 1 localhost 10000 &'], 
				shell=True,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
fcntl.fcntl(s.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
switches.append(s)

s = subprocess.Popen(['./UDPnode.py 2 localhost 10000'], 
				shell=True,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
fcntl.fcntl(s.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
switches.append(s)

i=0
# Pipe polling loop
while True:
	i += 1
	server.stdin.write('BOOTSTRAP ' + str(i))
	s.stdin.write('BOOTSTRAP ' + str(i))

	try:
		server_msg = server.stdout.read()
	except IOError:
		pass
	else:
		print >>sys.stdout, server_msg

	for switch in switches:
		try:
			switch_msg = switch.stdout.read()
		except IOError:
			pass
		else:
			print >>sys.stdout, switch_msg

	time.sleep(.01)