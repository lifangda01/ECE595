# Echo client program
import socket

HOST = '128.46.209.148'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
while 1:
	msg = raw_input('Enter message to send: ')
	s.sendall(msg)
	data = s.recv(1024)
	print 'Received', repr(data)
s.close()
