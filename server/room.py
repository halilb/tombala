import threading
import datetime
import random
import sys
from threading import Timer

from card import PlayCard

class Room(threading.Thread):
    def __init__(self, name, countdown):
        threading.Thread.__init__(self)
        self.name = name
        self.players = []
        self.hasStarted = False

        # generate game numbers
        self.futureNumbers = random.sample(range(1, 91), 90)
        self.oldNumbers = []

        now = datetime.datetime.now()
        self.startTime = now + datetime.timedelta(0, countdown)
        timer = Timer(countdown, self.startGame)
        timer.start()

    def startGame(self):
        print 'game started'
        self.hasStarted = True
        self.broadcastPlayerList()
        for player in self.players:
            playCard = PlayCard()
            player.setPlayCard(playCard)
        self.sendNewNumber()

    def sendNewNumber(self):
        allReady = True
        for player in self.players:
            if not player.readyForNewNumber:
                allReady = False

        if allReady:
            if len(self.futureNumbers) > 0:
                number = self.futureNumbers.pop()
                self.oldNumbers.append(number)
                body = {'number': number}

                for player in self.players:
                    player.broadcastMessage('BNUMBR', body)
                    player.readyForNewNumber = False

            else:
                print 'We are out of numbers. Something is wrong'

    def broadcastCinko(self, player, total):
        message = {
            'username': player.getUserName(),
            'total': total
        }
        for player in self.players:
            player.broadcastMessage('BCINKO', message)
            if total == 3:
                player.quitRoom()


    def addPlayer(self, player):
        self.players.append(player);
        self.broadcastPlayerList()

    def removePlayer(self, player):
        self.players.remove(player)
        self.broadcastPlayerList()

    def broadcastPlayerList(self):
        usernames = [x.getUserName() for x in self.players]
        message = {'userlist': usernames}
        for player in self.players:
            player.broadcastMessage('BUSRLS', message)


    def getDetails(self):
        response = {}
        response['roomname'] = self.name
        response['startTime'] = str(self.startTime)

        usernames = []
        for player in self.players:
            usernames.append(player.getUserName())
        response['userlist'] = usernames

        return response
