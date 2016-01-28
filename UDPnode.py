#!/usr/bin/env python
import socket, select
import sys, fcntl, os
import argparse
import pickle
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
switch = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Universal server socket
server_address = (args.ctrHostname, args.ctrPort)

# Input sockets to monitor
inputs = [ switch ]
# Output sockets to monitor
outputs = [ switch ]
# Exception of sockets to monitor
excepts = []

# Message buffer dictionary, destID : msg
msg_buffer_dict = {}

# Switch addresses, swID : swAddr
sw_addresses_dict = {}

# Called when REGISTER_RESPONSE is received
def _neighborUpdate(msg, addr):
	print 'Node %s - received: updated neighbors: %s' % (str(args.switchID), msg.content)

# Called when ROUTE_RESPONSE is received
def _packageForward(msg, addr):
	# Get the info of the next node
	nextID 		= msg.content[0]
	nextAddr 	= msg.content[1]
	destID 		= msg.content[2]
	print msg.content
	
	if nextAddr == None:
		return

	# Save the switch's address for future use
	sw_addresses_dict[nextID] = nextAddr

	# Get the pending message from buffer
	if destID in msg_buffer_dict:
		msg_out_pickled = msg_buffer_dict[destID]
		del msg_buffer_dict[destID]
	else:
		return
	
	sent = switch.sendto(msg_out_pickled, nextAddr)


def _generalReceive(msg, addr):
	print 'Node %s - received: general message %s' % (str(args.switchID), msg_in.content)

# Pool of functions to call when a message is received
receiveTable = {	REGISTER_RESPONSE: 	_neighborUpdate,
					ROUTE_RESPONSE:		_packageForward,
					GENERAL_MESSAGE:	_generalReceive	
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
		messageSend(ROUTE_REQUEST, args.switchID, 0, 1,
					[Destination])
		# Buffer the message
		msg_buffer_dict[Destination] = msg_out_pickled
		print 'Node %s - ERROR cannot find next address' % str(args.switchID)
		return

	sent = switch.sendto(msg_out_pickled, nextAddr)
	print 'Node %s - sent: type %s message to %s' % (str(args.switchID), str(Type), nextAddr)

# Register the switch to server
messageSend(REGISTER_REQUEST, args.switchID, 0, 1, [''])

i = 0
while True:
	i += 1
	# Wait for next msg to read/write
	readable, writable, exceptional = select.select(inputs, outputs, excepts)

	# # Send data
	# messageSend(GENERAL_MESSAGE, args.switchID, 2, 1, ['hello'])

	for socket in readable:
		data, address = switch.recvfrom(4096)	
		msg_in = pickle.loads(data)

		if msg_in.isValid():
			receiveTable[msg_in.type](msg_in, address)

	# The message to send back is determined by the message received
	for socket in writable:
		# if key.checkKey():
		# 	text = raw_input('Enter message to send: ')
		if args.switchID == 1:
			messageSend(GENERAL_MESSAGE, args.switchID, 2, 1, ['hello'])


	# # Receive response
	# data, address = switch.recvfrom(4096)
	# msg_in = pickle.loads(data)
	# receiveTable[msg_in.type](msg_in, address)

switch.close()






