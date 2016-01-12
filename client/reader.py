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
        print 'data ' + data
        print 'cmd ' + data[:5]
        print 'rest ' + data[7:]
        resType = data[:5]
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

            return body
        else:
            body['reqType'] = resType
            return body

    def testMessage(self, msg):
        msg = self.incoming_parser(msg)
        self.screenQueue(msg)

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            msg = self.incoming_parser(data)
            if msg:
                self.screenQueue.put(msg)
