import threading
import json


class Parser():
    def __init__(self):
        self.command = ''
        self.data = ''

    def clear(self):
        self.command = ''
        self.data = ''

    def parseMessage(self, client, message):
        self.clear()

        message = message.strip()
        self.command = message[:6]

        try:
            self.data = json.loads(message[7:])
            response = 'Command %s, data %s' % (self.command, self.data)
            print response
            sequence = self.data['seq']
            return 'SSUCCS:{"seq":%s}' % (sequence)

        except ValueError, e:
            print '%s when reading "%s"' % (str(e), message)
            return 'SERROR:{"message":"Wrong message format"}'


