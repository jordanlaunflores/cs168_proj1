import socket
import sys
import select
import utils

RECV_BUFFER = 200

class Client(object):

    def __init__(self, name, address, port):
    	self.name = name
        self.address = address
        self.port = int(port)
        self.socket = socket.socket()

        # Clients name is the first message sent to server
        try:
        	self.socket.connect((self.address, self.port))
        except:
        	error_message = utils.CLIENT_CANNOT_CONNECT.format(self.address, self.port)
        	sys.stdout.write(error_message + "\n")
        	sys.exit()
        init_msg = "/name " + name
        self.send_buffer(init_msg)

    def send_buffer(self, msg):
		while len(msg) < RECV_BUFFER:
			msg += " "
		self.socket.send(msg)

    def start(self):
    	while 1:
    		socket_list = [sys.stdin, self.socket]
    		ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
    		for sock in ready_to_read:
    			if sock == self.socket:
    				# message from server
    				data = sock.recv(RECV_BUFFER)
    				if data:
    					sys.stdout.write(data.strip())
    					#sys.stdout.write('[Me] ')
    				else:
    					error_message = utils.CLIENT_SERVER_DISCONNECTED.format(self.address, self.port)
    					sys.stdout.write(error_message)
    			else:
					# sending message
					msg = sys.stdin.readLine()
					print msg
					sys.stdout.write("Sending " + msg)
					self.send_buffer(msg)

args = sys.argv
if len(args) != 4:
    print "Please supply a name, a server address and port."
    sys.exit()
client = Client(args[1], args[2], args[3])
client.start()