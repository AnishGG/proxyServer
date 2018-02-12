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
	# print "reveived request is ", request

	# Get url of the website requested
	url = request.split()[1]
	print "url is ",url

	host_name = url.replace("www.","",1)
	portno_pos = host_name.find(":")
	portno = host_name[portno_pos+1:]
	print "host name is ", host_name
	print "port number is ", portno