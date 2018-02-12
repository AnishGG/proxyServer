import socket

port = 12345

# Create TCP socket
pServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Re-use the socket
pServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind
pServerSocket.bind(("", port))

pServerSocket.listen(7)

while True:
	print("here\n")
	conn, clientAddr = pServerSocket.accept()
	print "Client address is ", clientAddr

	# get the request from browser
	request = conn.recv(1024*1024)
	print "reveived request is ", request
