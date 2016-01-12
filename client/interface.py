import sys
from PyQt4.QtCore import * # NOQA
from PyQt4.QtGui import * # NOQA
from time import gmtime, strftime


class ClientDialog(QDialog):
    def __init__(self, threadQueue, screenQueue):
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue
        self.markedNumbers = []
        self.cinkoList = {}
        # create a Qt application --- every PyQt app needs one
        self.qt_app = QApplication(sys.argv)
        # Call the parent constructor on the current object
        QDialog.__init__(self, None)
        # Set up the window
        self.setWindowTitle('Tombala Client')
        self.setMinimumSize(500, 200)
        self.resize(640, 480)
        # Add a vertical layout
        self.vbox = QVBoxLayout()
        self.vbox.setGeometry(QRect(10, 10, 621, 461))
        # Add a horizontal layout
        self.hbox = QHBoxLayout()
        # The sender textbox
        self.sender = QLineEdit('', self)
        # The channel region
        self.channel = QTextBrowser()
        self.channel.setMinimumSize(QSize(240, 0))
        self.cardText = QTextBrowser()
        self.cardText.setMinimumSize(QSize(240, 0))
        # The send button
        self.send_button = QPushButton('&Send Command')
        self.next_button = QPushButton('&Next Number')
        # The users' section
        self.userList = QTextBrowser()
        self.rooms = QTextBrowser()
        # Connect the Go button to its callback
        self.send_button.clicked.connect(self.outgoing_parser)
        self.next_button.clicked.connect(self.next_number)
        # Add the controls to the vertical layout
        self.vbox.addLayout(self.hbox)
        self.hbox.addWidget(self.channel)
        self.vbox.addWidget(self.cardText)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        self.vbox.addWidget(self.next_button)
        self.hbox.addWidget(self.userList)
        self.hbox.addWidget(self.rooms)
        # start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateChannelWindow)
        # update every 10 ms
        self.timer.start(10)
        # Use the vertical layout for the current window
        self.setLayout(self.vbox)

        self.channel.append('Use /login {username} to log in')
        self.channel.append('Use /rooms to display available rooms')
        self.channel.append('Use /create {roomname} {countdow} to create a new game room')
        self.channel.append('Use /join {roomname} to join a room')
        self.channel.append('Use /mark {number} to mark a number in your playcard')
        self.channel.append('Use /announce {total} to announce cinko')
        self.channel.append('Use /quit to leave a room')

    def cprint(self, data):
        message = self.formatMessage(data, False)
        self.channel.append(message)

    def updateChannelWindow(self):
        if self.screenQueue.qsize() > 0:
            incoming_message = self.screenQueue.get()
            message = self.incoming_parser(incoming_message)

            if message:
                self.processIncoming(message)

    def displayRooms(self, rooms):
        text = ''
        for room in rooms:
            text += 'Room: %s ::: StartDate: %s ::: Players: %s\n' % (room['roomname'], room['startTime'], str(room['userlist']))

        self.rooms.setText(text)

    def updatePlayCard(self):
        text = ''
        for row in self.mycard:
            rowText = ''
            for number in row:
                rowText += str(number)
                if number in self.markedNumbers:
                    rowText += '*'
                rowText += '\t'

            text += rowText + '\n'

        self.cardText.setText(text)

    def processIncoming(self, data):
        print 'processIncoming ' + str(data)
        reqType = data['reqType']
        print 'processIncoming ' + reqType

        if reqType == 'CLOGIN':
            self.cprint(data['message'])

        elif reqType == 'CLROOM':
            self.displayRooms(data['rooms'])
        
        elif reqType == 'CJROOM':
            self.cprint('Joined the room!')

        elif reqType == 'CCROOM':
            self.cprint(data['message'])

        elif reqType == 'BGCAR':
            self.mycard = data['gamecard']
            self.updatePlayCard()

        elif reqType == 'BNUMBR':
            self.cprint('new number: ' + data['number'])

        elif reqType == 'MARK':
            self.markedNumbers.append(int(data['number']))
            self.updatePlayCard()

        elif reqType == 'BCINKO':
            username = data['username']
            self.cinkoList[username] = data['total']
            self.updatePlayers()

        elif reqType == 'BUSRLS':
            self.players = data['userlist']
            self.updatePlayers()


    def updatePlayers(self):
        text = ''
        for player in self.players:
            temp = player
            if player in self.cinkoList:
                total = self.cinkoList[player]
                temp = '%s(%s)' % (player, str(total))
            text += temp + '\n'

        self.userList.setText(text)

    def next_number(self):
        self.threadQueue.put('/next')

    def incoming_parser(self, mes):
        return mes

    def formatMessage(self, message, isLocal):
        result = strftime('%H:%M:%S', gmtime())
        result +=  ' -Local-' if isLocal else ' -Server-'
        return result + ': ' + message

    def outgoing_parser(self):
        msg = str(self.sender.text())
        if len(msg) > 0:
            displayedMessage = self.formatMessage(msg, True)
            self.channel.append(displayedMessage)
            self.sender.clear()
            self.threadQueue.put(msg)

    def run(self):
        ''' Run the app and show the main form. '''
        self.show()
        self.qt_app.exec_()
