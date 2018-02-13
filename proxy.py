import socket
import os
import re
import time

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

	line = "http://127.0.0.1:20000"
	matchobj = re.match(line, request.split()[1])
	if (matchobj):
		file_name = host_name[first_slash+1:]
		file_name = "/" + file_name
		print "file name is ", file_name
		words = request.split(" ")
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
	
	if os.path.isfile(file_name[1:]):
		print "File present in cache"
		# If the file is already present in the cache
		try:
			pAsClientMSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
			pAsClientMSocket.connect(('', port_no)) 
			fobj = open("." + file_name, "r")
			line_list = fobj.readlines()
			fobj.close()
			# prevdate = ""
			# for line in line_list:
				# if line.split(" ")[0] == "Last-Modified:":
					# prevdate = " ".join(line.split(" ")[1:])
			# prevdate = prevdate + "\n"
			# print "prevdate", prevdate
			print "file_name is", file_name
			prevdate = time.ctime(os.path.getmtime("."+file_name))
			print "prevdate", prevdate
			request_list = request.split("\n")

			for i in range(len(request_list)):
				if request_list[i] == "\r" or request_list[i] == "":
					continue
				if request_list[i].split()[0] == 'Host:':
					print "prevdate is ", prevdate
					modified_header = "If-Modified-Since: " + prevdate
					# modified_header = modified_header.strip("\n")
					# tmplist = modified_header.split()
					# tmp = tmplist[0] + " " + tmplist[1].strip(",") + " " + tmplist[3] + " " + tmplist[2] + " " + tmplist[5] + " " + tmplist[4]
					# modified_header = tmp

					print "modified_header", modified_header
					request_list.insert(i+1, modified_header)
			request = "\n".join(request_list)
			pAsClientMSocket.sendall(request)
			data = pAsClientMSocket.recv(1024)
			print "data is ", data	
			if data.split()[1] == "304":
				# File no modified in the server side, then retrieve the file from the cache
				print "Sending file from cache"
				fobj = open("." + file_name, "r")
				line_list = fobj.readlines()
				for line in line_list:
					conn.send(line)
			else:
				# File modified in the server, get the file from the server
				try:
					print "File modifed ... Retrieving file from server"
					fobj1 = open("files_stored","a+")
					stored_list = fobj1.readlines()
					stored_list = [line.strip("\n") for line in stored_list if line.strip() != '']
					fobj1.close()
					fobj1 = open("files_stored","w")
					print "stored_list", stored_list
					print "file_name", file_name
					stored_list.remove(file_name)
					print "here"
					os.remove(("."+file_name).strip("\n"))
					stored_list.append(file_name)
					print "FILES in cache are :", stored_list
					stored_list = [line for line in stored_list if line.strip() != '']
					fobj1.write("\n".join(stored_list))
					fobj1.close()
					fobj = open("." + file_name, "w")				# Sending ./ + filename
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

		except:
			print "Error connecting to server"
		


	else:   
		# If file not present in cache retrieve it from server
		# try:
		print "File not present in Cache ... Getting file from server"
		fobj1 = open("files_stored","a+")
		stored_list = fobj1.readlines()
		stored_list = [line for line in stored_list if line.strip() != '']
		fobj1.close()
		fobj1 = open("files_stored","w")
		if len(stored_list) >= 3:
			print "File to be removed from cache", stored_list[0]
			print "here ", "."+stored_list[0]
			os.remove(("."+stored_list[0]).strip("\n"))
			print "here"
			stored_list.pop(0)

		print "file_name is ", file_name
		stored_list.append(file_name)
		print "FILES in cache are :", stored_list
		stored_list = [line for line in stored_list if line.strip() != '']
		fobj1.write("\n".join(stored_list))
		fobj1.close()
		fobj = open("." + file_name, "w")                                               # Sending ./ + filename
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
		# except:
				# print "error connecting to the server"
