import select
import socket
import sys
import Queue

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'Server starting up on %s port %s' % server_address
server.bind(server_address)

# Input sockets to monitor
inputs = [ server ]
# Output sockets to monitor
outputs = [ server ]
# Exception of sockets to monitor
excepts = []

# Message queues for each live switch, indexed by address
msg_queues = {}

while True:
	# Wait for next msg to read/write
	print >>sys.stderr, "Waiting for next read/write..."
	readable, writable, exceptional = select.select(inputs, outputs, excepts)

	for socket in readable:
		
		data, address = server.recvfrom(4096)
		print >>sys.stderr, 'Server received %s bytes from %s' % (len(data), address)
		
		if data:
			# If the switch has just come alive
			if address not in msg_queues:
				msg_queues[address] = Queue.Queue()

			# Echo msg back by appending to the msg queue
			msg_queues[address].put(data)

	for socket in writable:
		for address in msg_queues
			# Send message if queue is not empty
			if not msg_queues[address].empty()
				data = msg_queues[address].get_nowait()
				sent = server.sendto(data, address)
				print >>sys.stderr, 'Server sent %s bytes back to %s' % (sent, address)