#!/usr/bin/env python
import select
import socket
import sys, fcntl, os
import Queue
import pickle
from UDPpackage import *

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'Server - starting up on %s port %s' % server_address
server.bind(server_address)

# Input sockets to monitor
inputs = [ server ]
# Output sockets to monitor
outputs = [ server ]
# Exception of sockets to monitor
excepts = []

# Message queues for each live switch, indexed by address
msg_queues = {}

# Response functions have the same interface: msg, addr
# Called when ROUTE_REQUEST
def routeTableLookUp(msg, addr):
	nextID = 2;
	switchID = msg.source
	# FIXME
	print 'Server - received ROUTE_REQUEST from node ' + str(switchID) 
	# TODO: add routing table stuff here
	# Assume the switch has already been registered

	msg_out = UDPpackage(ROUTE_RESPONSE,
						0, switchID,
						2,
						[nextID, addr])
	msg_out_pickled = pickle.dumps(msg_out)
	msg_queues[addr].put(msg_out_pickled)
	print 'Server - sent ROUTE_RESPONSE to node ' + str(switchID)


def routeTableUpdate():
	pass

# Called when REGISTER_REQUEST
def switchRegister(msg, addr):
	switchID = msg.source
	print 'Server - received REGISTER_REQUEST from node ' + str(switchID) 
	msg_queues[addr] = Queue.Queue()

	# TODO: add routing table stuff here

	msg_out = UDPpackage(REGISTER_RESPONSE,
						0, switchID,
						1,
						['TODO: neighbor_info_here'])
	msg_out_pickled = pickle.dumps(msg_out)
	msg_queues[addr].put(msg_out_pickled)
	print 'Server - sent REGISTER_RESPONSE to node ' + str(switchID)

def switchDelete(addr):
	pass

responseTable = {	REGISTER_REQUEST: 	switchRegister,
					ROUTE_REQUEST:		routeTableLookUp	
				}

while True:

	# Wait for next msg to read/write
	readable, writable, exceptional = select.select(inputs, outputs, excepts)

	for socket in readable:
		
		data, address = server.recvfrom(4096)
		print >>sys.stderr, 'Server - received %s bytes from %s' % (len(data), address)
		
		msg_in = pickle.loads(data)

		if msg_in.isValid():
			
			responseTable[msg_in.type](msg_in, address)

			# If the switch has just come alive
			# if address not in msg_queues:
			# 	msg_queues[address] = Queue.Queue()

			# Echo msg back by appending to the msg queue
			# msg_queues[address].put(data)

	# The message to send back is determined by the message received
	for socket in writable:
		for address in msg_queues:
			# Send message if queue is not empty
			if not msg_queues[address].empty():
				data = msg_queues[address].get_nowait()
				sent = server.sendto(data, address)
				print >>sys.stderr, 'Server - sent %s bytes back to %s' % (sent, address)

