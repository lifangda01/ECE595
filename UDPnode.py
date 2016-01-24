import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)
i = 0
while i < 10:
	i = i + 1
	# message = raw_input("Enter message: ")
	message = 'hello'

	# Send data
	sent = sock.sendto(message, server_address)

	# Receive response
	data, server = sock.recvfrom(4096)
	print "Received: ", data

sock.close()