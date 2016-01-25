import subprocess
import sys

# Setup host
server = subprocess.Popen('python UDPserver.py &', 
				shell=True, 
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)

# Setup switches
switches = []
s = subprocess.Popen(['python UDPnode.py 1 localhost 10000 &'], 
				shell=True,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
switches.append(s)
s = subprocess.Popen(['python UDPnode.py 2 localhost 10000 &'], 
				shell=True,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
switches.append(s)

# Pipe polling loop
while True:

	server_msg = server.stdout.readline()
	if server_msg:
		print >>sys.stdout, server_msg.rstrip()

	for switch in switches:
		switch_msg = switch.stdout.readline()
		if output:
			print >>sys.stdout, switch_msg.rstrip()

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