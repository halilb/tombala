import threading
import datetime

class Room(threading.Thread):
    def __init__(self, name, countdown):
        threading.Thread.__init__(self)
        self.name = name
        self.players = []
        now = datetime.datetime.now()
        self.startTime = now + datetime.timedelta(0, countdown)

    def addPlayer(self, player):
        print "player %s has joined to room %s: " % (player, self.name)
        self.players.append(player);

    def getDetails(self):
        response = {}
        response['roomname'] = self.name
        response['startTime'] = str(self.startTime)
        response['userlist'] = self.players
        return response
