#!/usr/bin/env python

import threading
import socket
import time
import json
import random

host = 'localhost'
port = 8888
global game_continues

game_continues = True

class Player (threading.Thread):
    def __init__(self, name, interval):
        threading.Thread.__init__(self)
        self.name = name
        self.interval = interval

    def run(self):
        name = self.name

        s = socket.socket()
        s.connect((host, port))

        reader = ReaderThread("ReaderThread%s" % (name), s, name)
        reader.start()
        writer = WriterThread("WriterThread%s" % (name), s, name, self.interval)
        writer.start()

        reader.join()
        writer.join()
        s.close()


class WriterThread (threading.Thread):
    def __init__(self, name, csoc, player, interval):
        threading.Thread.__init__(self)
        self.csoc = csoc
        self.player = player
        self.interval = interval

    def run(self):
        csoc = self.csoc
        player = self.player

        csoc.send('CLOGIN:{"seq":111,"username":"%s"}\n' % (player))
        csoc.send('CCROOM:{"seq":111,"roomname":"room1","countdown":1}\n')

        csoc.send('CJROOM:{"seq": 111,"roomname": "room1"}\n')
        csoc.send('CLROOM:{"seq":111}\n')

        global game_continues
        while game_continues:
            time.sleep(self.interval)
            csoc.send('CNNMBR:{"seq":111}\n')


class ReaderThread (threading.Thread):
    def __init__(self, name, csoc, player):
        threading.Thread.__init__(self)
        self.csoc = csoc
        self.player = player
        self.playCard = []
        self.oldNumbers = []
        self.cinkos = 0

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            if data:
                for message in data.split('\n'):
                    if len(message) > 0:
                        self.parse_incoming(message)
                        print 'incoming for %s: %s' % (self.player, data)
            else:
                break

    def parse_incoming(self, data):
        cmd = data[:6]
        body = json.loads(data[7:])

        if cmd == 'BNUMBR':
            number = body['number']
            self.checkNumber(number)
        elif cmd == 'BGCARD':
            self.playCard = body['gamecard']
            print 'card ' + str(self.playCard)
        elif cmd == 'BCINKO':
            username = body['username']
            total = body['total']
            print '%s toplam %i cinko yapti' % (username, total)
            if total == 3:
                global game_continues
                game_continues = False
                print 'game is over'

    def send_message(self, cmd, message):
        message['seq'] = random.randint(1, 1000)
        self.csoc.send('%s:%s' % (cmd, json.dumps(message)))

    def checkNumber(self, number):
        self.oldNumbers.append(number)
        total = 0
        for row in self.playCard:
            intersection = list(set(row) & set(self.oldNumbers))
            if len(intersection) == len(row):
                total += 1

        if total > self.cinkos:
            self.cinkos = total
            message = {'total': total}
            self.send_message('CCINKO', message)



player1 = Player("player1", 3)
player2 = Player("player2", 6)
player3 = Player("player3", 2)

player1.start()
player2.start()
player3.start()

player1.join()
player2.join()
player3.join()
