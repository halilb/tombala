import sys
from PyQt4.QtCore import * # NOQA
from PyQt4.QtGui import * # NOQA
from time import gmtime, strftime


class ClientDialog(QDialog):
    def __init__(self, threadQueue, screenQueue):
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue
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
        self.sender = QLineEdit("", self)
        # The channel region
        self.channel = QTextBrowser()
        self.channel.setMinimumSize(QSize(240, 0))
        self.card = QTextBrowser()
        self.card.setMinimumSize(QSize(240, 0))
        # The send button
        self.send_button = QPushButton('&Send Command')
        self.next_button = QPushButton('&Next Number')
        # The users' section
        self.userList = QTextBrowser()
        # Connect the Go button to its callback
        self.send_button.clicked.connect(self.outgoing_parser)
        self.next_button.clicked.connect(self.next_number)
        # Add the controls to the vertical layout
        self.vbox.addLayout(self.hbox)
        self.hbox.addWidget(self.channel)
        self.vbox.addWidget(self.card)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        self.vbox.addWidget(self.next_button)
        self.hbox.addWidget(self.userList)
        # start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateChannelWindow)
        # update every 10 ms
        self.timer.start(10)
        # Use the vertical layout for the current window
        self.setLayout(self.vbox)

    def cprint(self, data):
        self.channel.append(data)

    def updateChannelWindow(self):
        if self.screenQueue.qsize() > 0:
            incoming_message = self.screenQueue.get()
            message = self.incoming_parser(incoming_message)
            if message:
                message = self.formatMessage(message, False)
                self.channel.append(message)

    def next_number(self):
        print 'next number'

    def incoming_parser(self, mes):
        return 'incoming'

    def outgoing_parser(self):
        msg = str(self.sender.text())
        self.cprint(msg)
        self.sender.clear()

    def formatMessage(self, message, isLocal):
        result = strftime("%H:%M:%S", gmtime())
        result +=  " -Local-" if isLocal else " -Server-"
        return result + ": " + message

    def run(self):
        ''' Run the app and show the main form. '''
        self.show()
        self.qt_app.exec_()
