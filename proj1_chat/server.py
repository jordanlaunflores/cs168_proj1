import socket
import sys
import select
import utils

args = sys.argv
RECV_BUFFER = 200

class Server(object):
    
    def __init__(self, port):
        self.server_socket = socket.socket()
        self.server_socket.bind(("", int(port)))
        self.server_socket.listen(5)
        self.socket_list = [self.server_socket]
        self.port = int(port)
        self.socket_names = {}

        print "Chat server started on port " + str(port)
    
    def start(self):
        while True:
            
            ready_to_read,ready_to_write,in_error = select.select(self.socket_list,[],[],0)
            for sock in ready_to_read:
                # new connection
                if sock == self.server_socket:
                    (new_socket, address) = self.server_socket.accept()
                    self.socket_list.append(new_socket)
                    print "Client (%s, %s) connected" % address

                    self.broadcast(self.server_socket, new_socket, "[%s:%s] entered our chatting room\n" % address)

                # client message
                else:
                    try:
                        data = sock.recv(RECV_BUFFER).strip()
                        if data:
                            # data in socket
                            if data[0] == "/":
                                if data[:5] == "/name":
                                    sys.stdout.write(data[6:].strip() + " has just joined\n")
                                    #self.socket_names.add()
                                else:
                                    print "wat"
                            else:
                                sys.stdout.write(data)
                                #self.broadcast(self.server_socket, sock, data)
                        else:
                            # socket is broken
                            if sock in self.socket_list:
                                self.socket_list.remove(sock)
                            error_message = utils.SERVER_CLIENT_LEFT_CHANNEL.format(sock)
                            sys.stdout.write(error_message + "\n")
                            #self.broadcast(self.server_socket, sock, "Client (%s, %s) is offline\n" % address)

                    except:
                        if sock in self.socket_list:
                            self.socket_list.remove(sock)
                        #self.broadcast(self.server_socket, sock, "Client (%s, %s) is offline\n" % address)
                        error_message = utils.SERVER_CLIENT_LEFT_CHANNEL.format(sock)
                        sys.stdout.write(error_message + "\n")
                        continue

        self.server_socket.close()

    def broadcast(self, server_socket, sock, message):
        for socket in self.socket_list:
            # send the message only to peer
            if socket != self.server_socket and socket != sock:
                try :
                    socket.send(message)
                except :
                    # broken socket connection
                    print "broke"
                    socket.close()
                    # broken socket, remove it
                    if socket in self.socket_list:
                        self.socket_list.remove(socket)    

if len(args) != 2:
    print "Please supply a port."
    sys.exit()
server = Server(args[1])
server.start()
