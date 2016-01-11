import threading
import socket

class WriterThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue, screenQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue
        self.seq = 0

    def outgoing_parser(self, msg):
        return "outgoing"

    def run(self):
        while True:
            if self.threadQueue.qsize() > 0:
                queue_message = self.threadQueue.get()
                outgoing = self.outgoing_parser(queue_message)
                if outgoing:
                    outgoing += "\n"
                    print("OUTGOING: " + outgoing)
                    try:
                        self.csoc.send(outgoing)
                    except socket.error:
                        self.csoc.close()
                        break
