import threading
import socket
import signal
import json

from parser import Parser

signal.signal(signal.SIGINT, signal.SIG_DFL)

port = 8888
client_threads = []
rooms = []
client_count = 0

class Client(threading.Thread):
    def __init__(self, clientThreadID, client_socket):
        threading.Thread.__init__(self)
        self.clientThreadID = clientThreadID
        self.client_socket = client_socket
        self.username = ""
        self.connection_open = True
        self.parser = Parser(rooms)

    def run(self):
        while self.connection_open:
            data = self.client_socket.recv(1024)
            if len(data) == 0:
                self.connection_open = False
                break

            messages = data.split('\n')
            
            for message in messages:
                self.printMessage('message from client: ' + message)

                if len(message) > 0:
                    cmd, body = self.parser.parseMessage(self, message)
                    self.broadcastMessage(cmd, body)


        self.client_socket.close()
        self.room.removePlayer(self)
        client_threads.remove(self)

    def broadcastMessage(self, cmd, body):
        body = json.dumps(body)
        body = body.strip()
        message = cmd.strip() + ':' + body + '\n'
        self.client_socket.send(message)
        self.printMessage('response to client: {}'.format(message))

    def printMessage(self, text):
        print text, 'client_id: ',self.clientThreadID 

    def checkCinko(self, claim):
        if claim <= self.lastCinko:
            return False

        print 'old' + str(self.room.oldNumbers)
        real = self.playCard.calculateCinkos(self.room.oldNumbers)
        print 'real ' + str(real) + ' claim ' + str(claim)
        if claim == real:
            self.lastCinko = real
            self.room.broadcastCinko(self, real)

        return claim == real

    def getUserName(self):
        return self.username

    def setUsername(self, username):
        for client in client_threads:
            if client.getUserName() == username:
                return False
        self.username = username
        return True

    def setPlayCard(self, card):
        self.playCard = card
        self.broadcastMessage('BGCARD', card)

    def getRoomList(self):
        roomList = []
        for room in rooms:
            roomList.append(room.getDetails())
        return roomList

    def joinRoom(self, roomname):
        for room in rooms:
            if room.name == roomname:
                if not room.hasStarted:
                    room.addPlayer(self)
                    self.room = room
                    self.lastCinko = 0
                    return ''
                return 'Sorry, Game has already started'
        return 'Sorry, room is not found'

    def quitRoom(self):
        if self.room:
            self.room.removePlayer(self)
            self.room = None
            self.playCard = None
            self.parser.state = 'logged_in'
            return True
        return False


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
    client_thread = Client(client_count, c)
    client_thread.start()
    client_threads.append(client_thread)
    print 'Successfully created client thread', client_count-1
    serverThreadLock.release()
    print 'Successfully released server thread lock', client_count-1

sock.close()
