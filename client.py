from socket import *

host = "127.0.0.1"

print host

port= 7777

s=socket(AF_INET, SOCK_STREAM)

print "socket made"

s.connect((host,port))

print "socket connected!!!"


while True:
	data = raw_input("Enter data to be sent: ")
	s.send(data)
