import threading
import socket
import signal

from parser import Parser

signal.signal(signal.SIGINT, signal.SIG_DFL)

port = 8888
client_threads = []
rooms = []
client_count = 0

class ClientThread(threading.Thread):
    def __init__(self, clientThreadID, client_socket):
        threading.Thread.__init__(self)
        self.clientThreadID = clientThreadID
        self.client_socket = client_socket
        self.username = ""
        self.connection_open = True
        self.parser = Parser(rooms)

    def run(self):
        while self.connection_open:
            message = self.client_socket.recv(4096)
            self.printMessage('message from client: {}'.format(message))
            response = self.parser.parseMessage(self, message)
            self.printMessage('response to client: {}'.format(response))
            if response == '':
                break
            else:
                self.client_socket.send(response)
        self.client_socket.close()
        client_threads.remove(self)

    def printMessage(self, text):
        print text, 'client_id: ',self.clientThreadID 

    def getUsername(self):
        print "username requested ", self.username
        return self.username

    def setUsername(self, username):
        for client in client_threads:
            print client.getUsername()
            if client.getUsername() == username:
                return False
        self.username = username
        return True


serverThreadLock = threading.Lock()

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print "Server is started on port ", port
sock.bind(('', port)) 
sock.listen(5)

while True:
    c, addr = sock.accept()
    print 'Got connection from', addr            
    serverThreadLock.acquire()
    global client_count
    client_count = client_count + 1
    client_thread = ClientThread(client_count, c)
    client_thread.start()
    client_threads.append(client_thread)
    print 'Successfully created client thread', client_count-1
    serverThreadLock.release()
    print 'Successfully released server thread lock', client_count-1

sock.close()
