#!/usr/bin/env python
import select
import socket
import sys, fcntl, os
import Queue
import pickle
import threading
import argparse
from UDPpackage import *
from keyboardCapture import keyCapture
from SDNControllerUpdated import Graph

parser = argparse.ArgumentParser(description='Create a UDP controller.')

# Required arguments
parser.add_argument('ctrHostname', metavar='hostname',
					help="Hostname of the controller")
parser.add_argument('ctrPort', metavar='port', type=int,
					help="Port of the controller")

# Optional arguments
parser.add_argument('-v', action='store_true', default=False,
					help="Enable high verbosity")

args = parser.parse_args()

VERBOSE = args.v

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
# server_address = ('localhost', 10000)
server_address = (args.ctrHostname, args.ctrPort)
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
# Every switch in this table is active
sw_addresses_dict = {}

# Switch liviness, incremented when no TOPOLOGY_UPDATE received from node for K seconds
# swID : liviness
sw_liveness_dict = {}

# Initialize graph
graph = Graph()
# graph.calculate_all_neighbors()

# NeighborID graph, dict of list
# Should not be changed unless a new topology file
sw_neighbor_dict = {}
for key in graph.nbors_list:
	sw_neighbor_dict[int(key)] = map(int, list(graph.nbors_list[key]))

# Prepare to handle keyEvent
# key = keyCapture()

global initDone
initDone = 0

deadLinks = []

# Response functions have the same interface: msg, addr
# Called when ROUTE_REQUEST
def _handlerRouteRequest(msg, addr):
	# FIXME
	switchID = msg.source
	destID = msg.content[0]
	nextID = int(graph.calculate_next_hop(str(switchID), str(destID)));

	print 'Server - received: ROUTE_REQUEST from node ' + str(switchID) 
	# TODO: add routing table stuff here
	# Assume the switch has already been registered
	if nextID in sw_addresses_dict:
		nextAddr = sw_addresses_dict[nextID]
	else:
		nextAddr = None

	msg_out = UDPpackage(ROUTE_RESPONSE,
						SERVERID, switchID,
						3,
						# next switchID, next switch address and destID
						[nextID, nextAddr, destID])
	msg_out_pickled = pickle.dumps(msg_out)
	msg_queues_dict[addr].put(msg_out_pickled)
	print 'Server - sent: ROUTE_RESPONSE to node ' + str(switchID)

# Calculate next hops for all nodes
# Send ROUTE_UPDATE message to all nodes
def _sendRouteUpdate(deadlinks=[]):
	# Update the graph first
	activeIDs = list(sw_addresses_dict.keys())
	graph.update_graph( map(str, activeIDs), deadlinks )
	sw_neighbor_dict = {}
	for key in graph.nbors_list:
		sw_neighbor_dict[int(key)] = map(int, list(graph.nbors_list[key]))

	# Calculate next hops and send ROUTE_UPDATE per active node
	print sw_addresses_dict
	for activeID in sw_addresses_dict:
		nextHopsList = []
		for restActiveID in sw_addresses_dict:
			if restActiveID == activeID:
				continue
			nextHop = graph.calculate_next_hop(str(activeID), str(restActiveID))
			nextHopsList.append( (restActiveID, int(nextHop)) )

		msg_out = UDPpackage(ROUTE_UPDATE,
							SERVERID, activeID,
							3,
							nextHopsList)
		msg_out_pickled = pickle.dumps(msg_out)
		addr = sw_addresses_dict[activeID]
		msg_queues_dict[addr].put(msg_out_pickled)

# Called when REGISTER_REQUEST
def _handlerRegisterRequest(msg, addr):
	switchID = msg.source
	
	print 'Server - received: REGISTER_REQUEST from node %s %s' % (str(switchID), msg.content)
	
	# Only neighbors, not all switches!
	# (switchID, switchAddr)
	neighborInfoPairs = []
	# Prepare to send the active neighbor info back
	for neighborID in sw_neighbor_dict[switchID]:
		if neighborID in sw_addresses_dict:
			neighborInfoPairs.append( (neighborID, sw_addresses_dict[neighborID]) )

	# Set up the sending message queue for new switch
	# Also register the switch's address
	msg_queues_dict[addr] = Queue.Queue()
	sw_addresses_dict[switchID] = addr
	sw_liveness_dict[switchID] = 0
	# FIXME: add routing table stuff here

	# Clear Associate deadlinks of this new node
	global deadLinks
	deadLinks = [(f,t) for f,t in deadLinks if f!=str(switchID) and t!=str(switchID)]
	global initDone
	initDone = 0

	if initDone:
		_sendRouteUpdate(deadlinks=deadLinks)

	msg_out = UDPpackage(REGISTER_RESPONSE,
						SERVERID, switchID,
						1,
						neighborInfoPairs)
	msg_out_pickled = pickle.dumps(msg_out)
	msg_queues_dict[addr].put(msg_out_pickled)
	print 'Server - sent: REGISTER_RESPONSE to node ' + str(switchID)

def _handlerTopologyUpdate(msg, addr):
	switchID = msg.source
	
	if VERBOSE:
		print 'Server - received: TOPOLOGY_UPDATE from node %s %s' % (str(switchID), msg.content)

	activeNeighbors = []
	# List of active neighborID from msg.content
	for neighborID, neighborAddr in msg.content:
		activeNeighbors.append(neighborID)

	# Recharge liveness
	sw_liveness_dict[switchID] = 0
	
	# Any link is dead?
	global deadLinks
	if initDone > 1:
		for neighborID in sw_neighbor_dict[switchID]:
			# If not an active neighbor but live seen from controller, then the link is dead
			if neighborID not in activeNeighbors and neighborID in sw_addresses_dict:
				if (str(switchID), str(neighborID)) not in deadLinks:
					deadLinks.append( (str(switchID), str(neighborID)) )
				# sw_neighbor_dict[switchID].remove(neighborID)

		if deadLinks and _handlerTopologyUpdate.numDeadLinks != len(deadLinks):
			_sendRouteUpdate(deadlinks=deadLinks)
			print "Server - detected: link has failed", deadLinks

	# We got a new node?
	if switchID not in sw_addresses_dict:
		sw_addresses_dict[switchID] = addr
		sw_liveness_dict[switchID] = 0
		# FIXME: redo the topology calculation here
	_handlerTopologyUpdate.numDeadLinks = len(deadLinks)
_handlerTopologyUpdate.numDeadLinks = 0

# Pool of functions to call when a message is received
receiveTable = {	REGISTER_REQUEST: 	_handlerRegisterRequest,
					ROUTE_REQUEST:		_handlerRouteRequest,
					TOPOLOGY_UPDATE:	_handlerTopologyUpdate	
				}

# Age all the switches
def periodicSend():
	threading.Timer(Ksec, periodicSend).start()

	for neighborID in sw_addresses_dict:
		sw_liveness_dict[neighborID] += 1	

def periodicCheck():
	threading.Timer(Msec, periodicCheck).start()
	# Use a list to avoid size change of dict during loop
	inactiveList = []
	# Find dead switches (not links)
	for neighborID in sw_liveness_dict:
		if sw_liveness_dict[neighborID] > 3:
			print 'Server - detected: node %s has failed' % str(neighborID)
			inactiveList.append(neighborID)
			# Declare inactive
			del sw_addresses_dict[neighborID]
			# FIXME: redo the topology calculation here
	# Clean up
	for inactiveID in inactiveList:
		del sw_liveness_dict[inactiveID]
	# Send ROUTE_UPDATE to every live switch
	if inactiveList or len(sw_addresses_dict) != periodicCheck.numActiveSw:
		periodicCheck.numActiveSw = len(sw_addresses_dict)
		_sendRouteUpdate(deadlinks=deadLinks)
	global initDone
	initDone += 1
periodicCheck.numActiveSw = 0

# Initiate background periodic messages
periodicSend()
periodicCheck()

# _sendRouteUpdate()

while True:

	# key.checkKey()
	
	# Wait for next msg to read/write
	readable, writable, exceptional = select.select(inputs, outputs, excepts)

	for socket in readable:
		data, address = server.recvfrom(4096)
		# print >>sys.stderr, 'Server - received: %s bytes from %s' % (len(data), address)
		
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
				# print >>sys.stderr, 'Server - sent: %s bytes back to %s' % (sent, address)

