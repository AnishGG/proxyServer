import socket
import os

port = 12345

# Create TCP socket
pAsServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Re-use the socket
pAsServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind
pAsServerSocket.bind(("", port))

pAsServerSocket.listen(7)

while True:
    print("Proxy Server Ready\n")
    conn, clientAddr = pAsServerSocket.accept()
    print "Client address is ", clientAddr

    # get the request from browser
    request = conn.recv(1024*1024)
    # print "reveived request is ", request

    # Get url of the website requested
    print "request is ", request
    url = request.split()[1]
    print "url is ",url

    host_name = url.replace("www.","",1)
    port_no = -1

    http_pos = host_name.find("://") # find pos of ://
    if (http_pos != -1):
        host_name = host_name[(http_pos+3):] # get the rest of url

    port_pos = host_name.find(":") # find the port pos (if any)

    # find end of web server
    first_slash = host_name.find("/")

    if (request.split()[1] == "http://127.0.0.1:20000/1.txt"):
        file_name = host_name[first_slash+1:]
        file_name = "/" + file_name
        print "file name is ", file_name
        words = request.split(" ")
        print "words ", words
        words[1] = file_name
        request = " ".join(words)

    if first_slash == -1:
        first_slash = len(host_name)
    if (port_pos==-1 or first_slash < port_pos): 
        # default port 
        port_no = 80 
        host_name = host_name[:first_slash] 

    else: # specific port 
        port_no = int(host_name[(port_pos+1):(port_pos+1+(first_slash-port_pos-1))])
        host_name = host_name[:port_pos]

    print host_name, port_no
    
    print "file_name", file_name
    if os.path.isfile(file_name[1:]):
    	# If the file is already present in the cache
    	try:
			pAsClientMSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
			pAsClientMSocket.connect(('', port_no))	
			fobj = open("." + file_name, "r")
			line_list = fobj.readlines()
			fobj.close()
			prevdate = ""
			print "line_list", line_list
			for line in line_list:
				print "line", line
				if line.split(" ")[0] == "Date:":
					prevdate = " ".join(line.split(" ")[1:])
			prevdate = prevdate + "\n"
			print "prevdate :", prevdate
			request_list = request.split("\n")
			print "request list", request_list
			for i in range(len(request_list)):
				if request_list[i] == "\r" or request_list[i] == "":
					continue
				print "request_list[i]", request_list[i]
				if request_list[i].split()[0] == 'Host:':
					print "HOST DETECTED!"
					modified_header = "If-Modified-Since: " + prevdate
					modified_header = modified_header.strip("\n")
					print "modified_header is ", modified_header
					request_list.insert(i+1, modified_header)
			print "new request_list is ", request_list

			request = "\n".join(request_list)
			print "new request is ", request
			pAsClientMSocket.sendall(request)
			data = pAsClientMSocket.recv(1024)
			if data.split()[1] == "304":
				print "Sending file from cache"
				fobj = open("." + file_name, "r")
				line_list = fobj.readlines()
				for line in line_list:
				    conn.send(line)
			else:
				print "Not 304!!!"

        except:
            print "Error connecting to server"
    	


    else:	
    	# If file not present in cache retrieve it from server
    	try:
    		fobj = open("." + file_name, "w")												# Sending ./ + filename
        	pAsClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        	pAsClientSocket.connect(('', port_no))
        	pAsClientSocket.sendall(request)
        	while 1:
        	    # receive data from web server
        	    data = pAsClientSocket.recv(1024)
        	    print "data : ", data   
        	    fobj.write(data)

        	    if (len(data) > 0):
        	        conn.send(data) # send to browser/client
        	    else:
        	    	fobj.close()
        	        break
    	except:
			print "error connecting to the server"