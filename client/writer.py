import threading
import socket
import json
import traceback

class WriterThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue, screenQueue, messageList):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue
        self.messageList = messageList
        self.seq = 0

    def outgoing_parser(self, msg):
        reqType = ''
        message = {}

        if msg[0] == '/':
            words = msg.split(' ')
            cmd = words[0][1:]
            print 'cmd: ' + cmd
            if cmd == 'login':
                reqType = 'CLOGIN'
                message['username'] = words[1]

            elif cmd == 'rooms':
                reqType = 'CLROOM'

            elif cmd == 'join':
                reqType = 'CJROOM'
                message['roomname'] = words[1]

            elif cmd == 'create':
                reqType = 'CCROOM'
                message['roomname'] = words[1]
                message['countdown'] = int(words[2])

            elif cmd == 'next':
                reqType == 'CNNMBR'

            elif cmd == 'mark':
                message['reqType'] = 'MARK'
                message['number'] = words[1]
                self.screenQueue.put(message)
                return
            
            elif cmd == 'announce':
                message['reqType'] = 'CCINKO'
                message['total'] = int(words[1])

        if len(reqType) == 0:
            return

        message['seq'] = self.seq
        message['reqType'] = reqType

        self.seq += 1
        self.messageList.append(message)

        return '%s:%s' % (reqType, json.dumps(message))

    def run(self):
        while True:
            if self.threadQueue.qsize() > 0:
                queue_message = self.threadQueue.get()
                try:
                    outgoing = self.outgoing_parser(queue_message)
                    if outgoing:
                        outgoing += '\n'
                        print('OUTGOING: ' + outgoing)
                        try:
                            self.csoc.send(outgoing)
                        except socket.error:
                            self.csoc.close()
                            break
                except:
                    print(traceback.format_exc())
                    message = {
                        'reqType': 'SERROR',
                        'message': 'Invalid Command!'
                    }
                    self.screenQueue.put(message)
