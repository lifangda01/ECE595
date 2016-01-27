import select
import socket
import sys, fcntl, os
import Queue
import pickle
from UDPpackage import *

test_msg = UDPpackage(ROUTE_REQUEST,
                1, 2,
                3,
                ['hello world'])

test_msg_pickled = pickle.dumps(test_msg)

test_msg_unpickled = pickle.loads(test_msg_pickled)

print test_msg_unpickled.content