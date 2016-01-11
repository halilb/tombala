import threading
import json
import traceback

from room import Room

class Parser():
    def __init__(self, rooms):
        self.state = 'new'
        self.rooms = rooms

    def parseMessage(self, client, message):
        message = message.strip()
        command = message[:6]

        try:
            data = json.loads(message[7:])

            try:
                response = self.processCommand(client, command, data);
                isSuccess = response['type'] != 'err'
                resCode = 'SSUCCS' if isSuccess else 'SERROR'
                del response['type']

                return resCode, response
            except Exception, err:
                print(traceback.format_exc())
                return 'SERROR', {'message': 'Invalid command'}

        except ValueError, e:
            return 'SERROR', {'message': 'Wrong message format'}

    def processCommand(self, client, cmd, data):
        response = {}
        isError = False
        msg = ''

        if self.state == 'new':
            username = data['username']
            if client.setUsername(username):
                self.state = 'logged_in'
                msg = 'Welcome ' + username
            else:
                isError = True
                msg = '%s already exists on the system. Please choose another username!' % (username)

        elif cmd == 'CLROOM':
            response['rooms'] = client.getRoomList()

        elif self.state == 'logged_in':
            if cmd == 'CCROOM':
                roomname = data['roomname']
                newRoom = Room(roomname, data['countdown'])
                self.rooms.append(newRoom);
                msg = '%s is created' % (roomname);

            elif cmd == 'CJROOM':
                roomname = data['roomname']
                result = client.joinRoom(roomname)
                if len(result) == 0:
                    client.readyForNewNumber = True
                    self.state = 'in_game'
                else:
                    isError = True
                    msg = result


        elif self.state == 'in_game':
            if cmd == 'CNNMBR':
                if client.readyForNewNumber:
                    isError = True
                    msg = 'You already requested new number in this turn'
                else:
                    msg = 'Next number will be broadcasted when everyone proceeds!'
                    client.readyForNewNumber = True
                    client.room.sendNewNumber()

            elif cmd == 'CQROOM':
                roomName = client.room.name
                if client.quitRoom():
                    msg = 'You have left room ' + roomName
                    self.state = 'logged_in'
                else:
                    isError = True
                    msg = 'You are not in a room currently'

            elif cmd == 'CCINKO':
                total = data['total']
                if client.checkCinko(total):
                    msg = 'Congratulations!'
                else:
                    isError = True
                    msg = 'Your cinko claim is wrong!'


        response['type'] = 'err' if isError else 'success'
        response['seq'] = data['seq']
        if len(msg):
            response['message'] = msg

        return response
