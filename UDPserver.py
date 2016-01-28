#!/usr/bin/env python
import select
import socket
import sys, fcntl, os
import Queue
import pickle
from UDPpackage import *
from keyboardCapture import keyCapture

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

# Message queues for each live switch, addr : msgQ
msg_queues_dict = {}

# Switch addresses, swID : swAddr
sw_addresses_dict = {}

# Prepare to handle keyEvent
# key = keyCapture()

# Response functions have the same interface: msg, addr
# Called when ROUTE_REQUEST
def _routeTableLookUp(msg, addr):
	# FIXME
	nextID = 2;
	switchID = msg.source
	destID = msg.content[0]

	print 'Server - received: ROUTE_REQUEST from node ' + str(switchID) 
	# TODO: add routing table stuff here
	# Assume the switch has already been registered
	if nextID in sw_addresses_dict:
		nextAddr = sw_addresses_dict[nextID]
	else:
		nextAddr = None

	msg_out = UDPpackage(ROUTE_RESPONSE,
						0, switchID,
						3,
						# next switchID, next switch address and destID
						[nextID, nextAddr, destID])
	msg_out_pickled = pickle.dumps(msg_out)
	msg_queues_dict[addr].put(msg_out_pickled)
	print 'Server - sent: ROUTE_RESPONSE to node ' + str(switchID)


def _routeTableUpdate():
	pass

# Called when REGISTER_REQUEST
def _switchRegister(msg, addr):
	switchID = msg.source
	
	print 'Server - received: REGISTER_REQUEST from node ' + str(switchID) 
	
	# Set up the sending message queue for new switch
	# Also register the switch's address
	msg_queues_dict[addr] = Queue.Queue()
	sw_addresses_dict[switchID] = addr

	# TODO: add routing table stuff here

	msg_out = UDPpackage(REGISTER_RESPONSE,
						0, switchID,
						1,
						['TODO: neighbor_info_here'])
	msg_out_pickled = pickle.dumps(msg_out)
	msg_queues_dict[addr].put(msg_out_pickled)
	print 'Server - sent: REGISTER_RESPONSE to node ' + str(switchID)

def _switchDelete(addr):
	pass

# Pool of functions to call when a message is received
receiveTable = {	REGISTER_REQUEST: 	_switchRegister,
					ROUTE_REQUEST:		_routeTableLookUp	
				}

while True:

	# key.checkKey()
	
	# Wait for next msg to read/write
	readable, writable, exceptional = select.select(inputs, outputs, excepts)

	for socket in readable:
		data, address = server.recvfrom(4096)
		print >>sys.stderr, 'Server - received: %s bytes from %s' % (len(data), address)
		
		msg_in = pickle.loads(data)

		if msg_in.isValid():
			receiveTable[msg_in.type](msg_in, address)

	# The message to send back is determined by the message received
	for socket in writable:
		for address in msg_queues_dict:
			# Send message if queue is not empty
			if not msg_queues_dict[address].empty():
				data = msg_queues_dict[address].get_nowait()
				sent = server.sendto(data, address)
				print >>sys.stderr, 'Server - sent: %s bytes back to %s' % (sent, address)

