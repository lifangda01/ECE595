#!/usr/bin/env python
import socket, select
import sys, fcntl, os
import argparse
import pickle
import threading
from UDPpackage import *
from keyboardCapture import keyCapture

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

# Prepare to handle keyEvent
# key = keyCapture()

# Create a UDP socket
SWITCHID = args.switchID
switch = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Universal server socket
server_address = (args.ctrHostname, args.ctrPort)

# Link failure?
LINKFAILID = args.f

# Input sockets to monitor
inputs = [ switch ]
# Output sockets to monitor
outputs = [ switch ]
# Exception of sockets to monitor
excepts = []

# Message buffer dictionary, destID : msg
msg_buffer_dict = {}

# Switch addresses, swID : swAddr
# Every switch in this dict is a neighbor
sw_addresses_dict = {}

# Switch liviness, incremented when no KEEP_ALIVE received from node for K seconds
# swID, liviness
sw_liveness_dict = {}

# Called when REGISTER_RESPONSE is received
def _handlerRegisterResponse(msg, addr):
	print 'Node %s - received: REGISTER_RESPONSE %s' % (str(SWITCHID), msg.content)

	# Add new neighbors
	for (neighborID, neighborAddr) in msg.content:
		sw_addresses_dict[neighborID] = neighborAddr
		sw_liveness_dict[neighborID] = 0
		messageSend(KEEP_ALIVE, SWITCHID, neighborID, 1, [(SWITCHID, SWITCHADDR)])


# Called when ROUTE_RESPONSE is received
def _handlerRouteResponse(msg, addr):
	# Get the info of the next node
	nextID 		= msg.content[0]
	nextAddr 	= msg.content[1]
	destID 		= msg.content[2]
	print msg.content
	
	if nextAddr == None:
		return

	# Save the switch's address for future use, it's gonna be one of the neighbors
	sw_addresses_dict[nextID] = nextAddr
	sw_liveness_dict[nextID] = 0

	# Get the pending message from buffer
	if destID in msg_buffer_dict:
		msg_out_pickled = msg_buffer_dict[destID]
		del msg_buffer_dict[destID]
	else:
		return
	
	sent = switch.sendto(msg_out_pickled, nextAddr)

def _handlerKeepAlive(msg, addr):
	if msg.source == LINKFAILID:
		return
	print 'Node %s - received: KEEP_ALIVE from node %s' % (str(SWITCHID), msg.source)
	
	# Recharge liveness
	sw_liveness_dict[msg.source] = 0

	# Store source node if not already
	if msg.source not in sw_addresses_dict:
		sw_addresses_dict[msg.source] = addr
		# Tell server we have discovered a new neighbor
		# (switchID, switchAddr)
		neighborInfoPairs = []	
		for neighborID in sw_addresses_dict:
			neighborInfoPairs.append( (neighborID, sw_addresses_dict[neighborID]) )
		# Send TOPOLOGY_UPDATE along with neighbor info to server
		messageSend(TOPOLOGY_UPDATE, SWITCHID, SERVERID, 1, neighborInfoPairs)

def _handlerGeneralMessage(msg, addr):
	print 'Node %s - received: GENERAL_MESSAGE %s' % (str(SWITCHID), msg_in.content)

# Pool of functions to call when a message is received
receiveTable = {	REGISTER_RESPONSE: 	_handlerRegisterResponse,
					ROUTE_RESPONSE:		_handlerRouteResponse,
					GENERAL_MESSAGE:	_handlerGeneralMessage,
					KEEP_ALIVE:			_handlerKeepAlive	
				}

# General function to call when sending a message
def messageSend(Type, Source, Destination, Length, Content):
	msg_out = UDPpackage(Type, Source, Destination, Length, Content)
	msg_out_pickled = pickle.dumps(msg_out)

	if Destination == 0:
		nextAddr = server_address
	elif Destination in sw_addresses_dict:
		nextAddr = sw_addresses_dict[Destination]
	else:
		# Query the server for next node to go
		messageSend(ROUTE_REQUEST, SWITCHID, 0, 1,
					[Destination])
		# Buffer the message
		msg_buffer_dict[Destination] = msg_out_pickled
		print 'Node %s - ERROR cannot find next address' % str(SWITCHID)
		return

	sent = switch.sendto(msg_out_pickled, nextAddr)
	# print 'Node %s - sent: type %s message to %s' % (str(SWITCHID), str(Type), nextAddr)

# Send KEEP_ALIVE to neighbors and TOPOLOGY_UPDATE to server
def periodicSend():
	threading.Timer(Ksec, periodicSend).start()

	# (switchID, switchAddr)
	neighborInfoPairs = []	
	# Send KEEP_ALIVE to each cached/active neighbor
	for neighborID in sw_addresses_dict:
		if neighborID == LINKFAILID:
			continue
		messageSend(KEEP_ALIVE, SWITCHID, neighborID, 0, [])
		neighborInfoPairs.append( (neighborID, sw_addresses_dict[neighborID]) )
		sw_liveness_dict[neighborID] += 1

	# Send TOPOLOGY_UPDATE along with neighbor info to server
	messageSend(TOPOLOGY_UPDATE, SWITCHID, SERVERID, 1, neighborInfoPairs)

# Check for inactive switches
def periodicCheck():
	threading.Timer(Msec, periodicCheck).start()
	
	# Use a list to avoid size change of dict during loop
	inactiveList = []
	for neighborID in sw_liveness_dict:
		if sw_liveness_dict[neighborID] > 3:
			inactiveList.append(neighborID)
			# Declare inactive
			del sw_addresses_dict[neighborID]
			# (switchID, switchAddr)
			neighborInfoPairs = []	
			for activeID in sw_addresses_dict:
				neighborInfoPairs.append( (activeID, sw_addresses_dict[activeID]) )
			# Send TOPOLOGY_UPDATE along with neighbor info to server
			messageSend(TOPOLOGY_UPDATE, SWITCHID, SERVERID, 1, neighborInfoPairs)
	# Clean up
	for inactiveID in inactiveList:
		del sw_liveness_dict[inactiveID]

# Register the switch to server
messageSend(REGISTER_REQUEST, SWITCHID, SERVERID, 0, [])

SWITCHADDR = (socket.gethostbyname(socket.gethostname()), switch.getsockname()[1])
print 'Node %s - created: %s' % (SWITCHID, SWITCHADDR)

# Initiate background periodic messages
periodicSend()
periodicCheck()

while True:
	# Wait for next msg to read/write
	readable, writable, exceptional = select.select(inputs, outputs, excepts)

	for socket in readable:
		data, address = switch.recvfrom(4096)	
		msg_in = pickle.loads(data)

		if msg_in.isValid():
			receiveTable[msg_in.type](msg_in, address)

	# The message to send back is determined by the message received
	for socket in writable:
		pass

switch.close()






