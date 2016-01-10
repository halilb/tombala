#!/usr/bin/env python

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8888))

sock.send('CLOGIN:{"seq":111,"username":"user1"}\n')
sock.send('CCROOM:{"seq":111,"roomname":"room1","countdown":120}\n')
sock.send('CJROOM:{"seq": 111,"roomname": "room1"}\n')
sock.send('CLROOM:{"seq":111}\n')

while True:
    data = sock.recv(1024)
    if data:
        print 'incoming: ', data
    else:
        break
