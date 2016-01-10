import threading

class Room(threading.Thread):
    def __init__(self, name, countdown):
        threading.Thread.__init__(self)
        self.name = name
        self.countdown = countdown
        self.players = []

    def addPlayer(self, player):
        print "player %s has joined to room %s: " % (player.getUsername(), self.name)
        self.players.append(player);
