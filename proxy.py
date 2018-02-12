import socket

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
    
    try:
        pAsClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        pAsClientSocket.connect(('', port_no))
        pAsClientSocket.sendall(request)
            
        while 1:
            # receive data from web server
            data = pAsClientSocket.recv(1024)
            print "data : ", data   

            if (len(data) > 0):
                conn.send(data) # send to browser/client
            else:
                break
    except:
        print "error connecting to the server"
