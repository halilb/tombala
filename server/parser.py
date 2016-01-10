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
                return '%s:%s' % (resCode, response)
            except Exception, err:
                print(traceback.format_exc())
                return 'SERROR:{"message":"Invalid command"}'

        except ValueError, e:
            print '%s when reading "%s"' % (str(e), message)
            return 'SERROR:{"message":"Wrong message format"}'

    def processCommand(self, client, cmd, data):
        response = {}
        isError = False
        msg = ''

        if self.state == 'new':
            username = data['username']
            if client.setUsername(username):
                self.state = 'logged_in'
                msg = 'Welcome ', username
            else:
                isError = True
                msg = '%s already exists on the system. Please choose another username!' % (username)

        elif self.state == 'logged_in':
            if cmd == 'CCROOM':
                roomname = data['roomname']
                newRoom = Room(roomname, data['countdown'])
                self.rooms.append(newRoom);
                msg = '%s is created' % (roomname);

            elif cmd == 'CJROOM':
                roomname = data['roomname']
                client.joinRoom(roomname)
                self.state = 'in_room'

        elif cmd == 'CLROOM':
            response['rooms'] = client.getRoomList()

        response['type'] = 'err' if isError else 'success'
        response['seq'] = data['seq']
        if len(msg):
            response['message'] = msg

        return response
