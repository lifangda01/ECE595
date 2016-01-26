import subprocess
import time
import fcntl
import os, sys

test = subprocess.Popen(['cat'], 
                shell=True, 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)

fcntl.fcntl(test.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

i = 0
while True:
    i += 1
    test.stdin.write('hello ' + str(i))

    try:
        msg = test.stdout.read()
    except IOError:
        pass
    else:
        print >>sys.stdout, msg

    time.sleep(0.1)