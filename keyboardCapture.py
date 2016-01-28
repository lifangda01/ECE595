import termios, fcntl, sys, os

class keyCapture(object):
	def __init__(self):
		super(keyCapture, self).__init__()
		self.fd = sys.stdin.fileno()

		self.oldterm = termios.tcgetattr(self.fd)
		self.newattr = termios.tcgetattr(self.fd)
		self.newattr[3] = self.newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(self.fd, termios.TCSANOW, self.newattr)

		self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
		fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)
		
	def checkKey(self):
		try:
			c = sys.stdin.read(1)
			print "Got character", repr(c)
		except IOError: 
			return None
		else:
			return c

	def finish(self):
		termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)
		fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)