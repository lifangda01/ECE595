import subprocess
import os, sys, fcntl
import time

# Setup host
server = subprocess.Popen(['python',' -u UDPserver.py &'], 
# server = subprocess.Popen(['python -u UDPserver.py &'], 
				shell=True, 
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
# Make read non-blocking, raise an IOError if msg is empty
fcntl.fcntl(server.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

# Setup switches
switches = []
s = subprocess.Popen(['python -u UDPnode.py 1 localhost 10000 &'], 
				shell=True,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
fcntl.fcntl(s.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
switches.append(s)

s = subprocess.Popen(['python -u UDPnode.py 2 localhost 10000 &'], 
				shell=True,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
fcntl.fcntl(s.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
switches.append(s)

# Pipe polling loop
while True:

	# server.stdin.write('hello' + '\n')

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

# # Setup host
# subprocess.call(['python UDPserver.py &'], shell=True)

# # Setup switches
# subprocess.call(['python UDPnode.py 1 localhost 10000 &'], shell=True)
# subprocess.call(['python UDPnode.py 2 localhost 10000 &'], shell=True)

# while True:
# 	msg = raw_input("Enter message: ")


# parent stdin to child stdin, child stdout & stderr to parrent stdout
# proc = subprocess.Popen('cat -; echo "to stderr" 1>&2',
#                         shell=True,
#                         stdin=subprocess.PIPE,
#                         stdout=subprocess.PIPE,
#                         stderr=subprocess.STDOUT,
#                         )
# stdout_value, stderr_value = proc.communicate('through stdin to stdout\n')

# readline() gets the output one line each time
# communicate() gets everything all at once
# communicate() waits for process to terminate!!!!
# print 'One line at a time:'
# proc = subprocess.Popen('python repeater.py', 
#                         shell=True,
#                         stdin=subprocess.PIPE,
#                         stdout=subprocess.PIPE,
#                         )
# for i in range(10):
#     proc.stdin.write('%d\n' % i)
#     output = proc.stdout.readline()
#     print output.rstrip()
# remainder = proc.communicate()[0]
# print remainder # remainder is empty