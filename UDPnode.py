#!/usr/bin/env python
import socket
import sys, fcntl, os
import argparse

parser = argparse.ArgumentParser(description='Create a UDP switch.')

# Required arguments
parser.add_argument('switchID', metavar='id', type=int,
					help="ID of the switch")
parser.add_argument('ctrHostname', metavar='hostname',
					help="Hostname of the controller")
parser.add_argument('ctrPort', metavar='port', type=int,
					help="Port of the controller")

# Optional arguments
parser.add_argument('-f', metavar='nid', type=int,
					help="ID of neighbor switch on the failed link")

args = parser.parse_args()

# Create a UDP socket
switch = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (args.ctrHostname, args.ctrPort)

# Make stdin.read() non-blocking
fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

while True:

	# try:
	# 	msg = sys.stdin.read()
	# except IOError:
	# 	pass
	# else:
	# 	print >>sys.stderr, msg

	message = str(args.switchID)

	# Send data
	sent = switch.sendto(message, server_address)

	# Receive response
	data, server = switch.recvfrom(4096)
	print >>sys.stderr, 'Node %s - received: %s' % (str(args.switchID), data)

switch.close()