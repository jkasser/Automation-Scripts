import socket
import sys
from thread import *

host = "127.0.0.1"
port = 7777

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print "Socket Created"

# Try to bind the socket to a local host and port
try:
	s.bind((host,port))
	print "Socket Bound"
except socket.error as msg:
	print 'Bind failed. Error Code:', str(msg[0]), 'Message', str(msg[1])
	sys.exit()


# Start listening on the socket
s.listen(10)
print "Listening for connections..."

# Wait to accept a connection
conn,addr = s.accept()
print 'Connected with', str(addr[0]), ':', str(addr[1])

# Keep talking with the client
while True:
	msg=conn.recv(1024)
	print "Message from client : " + msg
	if 'shutdown' in msg.lower():
		conn.close()
	else:
		conn.send(msg)

	if not msg:
		break
