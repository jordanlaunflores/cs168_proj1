import socket
import sys
import select
import utils

args = sys.argv
RECV_BUFFER = 200

class Server(object):
    
    def __init__(self, port):
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	self.server_socket.bind(("", int(port)))
        self.server_socket.listen(5)
        self.socket_list = [self.server_socket]
        self.port = int(port)
	
	# maps sockets to client objects
        self.clients = {}
	
	# maps channel names to channel objects
	self.channels = set()
    
    def start(self):
        while True:
            
            ready_to_read,ready_to_write,in_error = select.select(self.socket_list,[],[],0)
            for sock in ready_to_read:
                # new connection
                if sock == self.server_socket:
                    (new_socket, address) = self.server_socket.accept()
                    self.socket_list.append(new_socket)
		    new_client = Client(new_socket)
		    self.clients[new_socket] = new_client

                # client message
                else:
#                    try:
                        data = sock.recv(RECV_BUFFER)
			if data:
                            # data in socket
			    if len(data.strip()) == 0:
				continue
			    
			    data = data.strip()
			    if data[0] == "/":
				# command is sent
				if data[:5] == "/name":
				    client = self.clients[sock]
				    client.name = data[6:].strip()
				
				elif data[:5] == "/join":
				    channel_name = data[6:].strip()
				    if channel_name in self.channels:
					client = self.clients[sock]
					if client.channel == channel_name:
					    error_message = "Cannot join channel you are currently in\n"
					    self.send_buffer(error_message, sock)
					    continue
					client.channel = channel_name
					# tell channel that client has joined
					msg = utils.SERVER_CLIENT_JOINED_CHANNEL.format(client.name)
					self.broadcast(sock, ":==" + msg)
				    elif not channel_name:
					error_message = utils.SERVER_JOIN_REQUIRES_ARGUMENT
					self.send_buffer(error_message, sock)
				    else:
					error_message = utils.SERVER_NO_CHANNEL_EXISTS.format(channel_name) + "\n"
					self.send_buffer(error_message, sock)
				
				elif data[:7] == "/create":
				    channel_name = data[8:].strip()
				    if channel_name in self.channels:
					error_message = utils.SERVER_CHANNEL_EXISTS.format(channel_name) + "\n"
					self.send_buffer(error_message, sock)
				    elif not channel_name:
					error_message = utils.SERVER_CREATE_REQUIRES_ARGUMENT + "\n"
					self.send_buffer(error_message, sock)
				    else:
					client = self.clients[sock]
					if client.channel:
					    # tell current channel client is leaving
					    msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(client.name) + "\n"
					    self.broadcast(sock, ":==" + msg)
					client.channel = channel_name
					self.channels.add(channel_name)
				
				elif data[:5] == "/list":
				    for channel_name in self.channels:
					self.send_buffer(channel_name + "\n", sock)
				
				else:
                                    error_message = utils.SERVER_INVALID_CONTROL_MESSAGE.format(data) + "\n"
				    self.send_buffer(error_message, sock) 

			    else:
				# regular message is sent
                                self.broadcast(sock, data + "\n")

                        else:
                            # socket is broken
                            if sock in self.socket_list:
                                self.socket_list.remove(sock)
			    client = self.clients[sock]
                            error_message = utils.SERVER_CLIENT_LEFT_CHANNEL.format(client.name) + "\n"
                            self.broadcast(sock, ":==" + error_message)

#		    except:
#			# socket is broken
#                        if sock in self.socket_list:
#                            self.socket_list.remove(sock)
#			client = self.clients[sock]
#                        error_message = utils.SERVER_CLIENT_LEFT_CHANNEL.format(client.name) + "\n"
#                        self.broadcast(sock, ":==" + error_message)
#                        continue

        self.server_socket.close()

    def broadcast(self, socket, msg):
	client = self.clients[socket]
	if client.channel == "":
	    error_message = utils.SERVER_CLIENT_NOT_IN_CHANNEL + "\n"
	    self.send_buffer(error_message, socket)
	    return
	for sock in self.socket_list:
	    if sock != socket and sock != self.server_socket:
		c = self.clients[sock]
	    	if c.channel == client.channel:
		    try:
			if msg[:3] == ":==":
			    # sending utils message
			    self.send_buffer(msg[3:], sock)
			else:
		            msg = "[" + client.name + "] " + msg + "\n"
		            self.send_buffer(msg, sock)
		    except:
			# broken socket connection
			sock.close()
			if sock in self.socket_list:
			    self.socket_list.remove(sock)


    def send_buffer(self, msg, socket):
	while len(msg) < RECV_BUFFER:
	    msg += " "
	socket.send(msg)


class Client(object):

    def __init__(self, socket):
	self.socket = socket
	self.name = ""
	self.channel = ""
	self.buff = ""

if len(args) != 2:
    print "Please supply a port."
    sys.exit()
server = Server(args[1])
server.start()
