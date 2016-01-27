#!/usr/bin/env python
import socket
import sys, fcntl, os
import argparse
import pickle
from UDPpackage import *

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

# Register the switch
msg_out = UDPpackage(REGISTER_REQUEST,
					args.switchID, 0,
					1,
					[''])
msg_out_pickled = pickle.dumps(msg_out)
sent = switch.sendto(msg_out_pickled, server_address)

while True:

	# Send data
	sent = switch.sendto(msg_out_pickled, server_address)

	# Receive response
	data, server = switch.recvfrom(4096)
	msg_in = pickle.loads(data)
	print >>sys.stderr, 'Node %s - received: %s' % (str(args.switchID), msg_in.content)

switch.close()