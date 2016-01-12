import threading
import json


class ReaderThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue, screenQueue, messageList):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ''
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue
        self.messageList = messageList

    def incoming_parser(self, data):
        print 'data:' + data
        print 'cmd:' + data[:6]
        print 'rest:' + data[7:]
        resType = data[:6]

        print 'EXCEPTIONOLACAK' + data[7:]
        body = json.loads(data[7:])
        seq = -1

        if 'seq' in body:
            seq = body['seq']

        print 'body ' +  str(body)

        if seq > -1: # request-response type
            isSuccess = resType == 'SSUCCS'
            request = self.messageList[seq]
            reqType = request['reqType']
            body['reqType'] = reqType
            body['isSuccess'] = isSuccess

            return body
        else:
            body['reqType'] = resType
            body['isSuccess'] = True
            return body

    def testMessage(self, msg):
        msg = self.incoming_parser(msg)
        self.screenQueue(msg)

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            if data:
                for message in data.split('\n'):
                    if len(message) > 0:
                        message = self.incoming_parser(message)
                        self.screenQueue.put(message)
            else:
                break
