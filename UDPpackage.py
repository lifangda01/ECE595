GENERAL_MESSAGE		= 0
REGISTER_REQUEST 	= 1		# NULL
REGISTER_RESPONSE 	= 2		# (neigID, neigAddr), ...
KEEP_ALIVE 			= 3		# (currID, currAddr), ...
ROUTE_UPDATE		= 4		# (destID, nextID), ...
TOPOLOGY_UPDATE		= 5		# (neigID, neigAddr), ...
ROUTE_REQUEST		= 6		# destID
ROUTE_RESPONSE		= 7		# nextID, nextAddr, destID

# Used for periodic functions
Ksec 				= 1.0
Msec 				= 5.0

SERVERID 			= 0

ACTIVE 				= 1
INACTIVE			= 0

# An object representing an actual message
# ID of server is 0
class UDPpackage(object):

	def __init__(self, Type, Source, Destination, Length, Content):
		self.type = Type
		self.source = Source
		self.destination = Destination
		self.length = Length
		self.content = Content
		return

	def isValid(self):
		return self.type < 8