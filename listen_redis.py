#!/usr/bin/env python
import sys
import redis
from PyQt4 import QtGui
from PyQt4.QtCore import *

# local config file
import config

# TODO: better icons (these were lifted from KDE4 Oxygen theme)
IDLE_ICON="idle.png"
MESSAGE_ICON="message.png"
# TODO: error icon for connection troubles

# how long to show the message bubble
MESSAGE_TIMEOUT=1000

class ListenThread(QThread):
    new_message = pyqtSignal(str,str,name='newMessage')
    clear = pyqtSignal(name='clear')

    def __init__(self):
        print "in other thread"
        QThread.__init__(self)
        # self.setDaemon(False)

    def run(self):
        print "connecting to redis..."
        # TODO: use paramiko or shell out to ssh to establish tunnel?
        r = redis.StrictRedis(
                host=config.redis['server'],
                port=config.redis['port'],
                password=config.redis['password'],
                db=0
            )
        ps = r.pubsub()
        ps.subscribe(['irssi'])

        print "subscribing to irssi topic on redis"
        for item in ps.listen():
            print item
            msg = str(item['data']).partition('  ')
            print "PIECES: ", msg
            if item['type'] == 'message':
                if msg[0] == '__CLEAR__':
                    # my irssi script sends this special __CLEAR__ code
                    # when there's a keypress in irssi since last message posted
                    self.clear.emit()
                elif len(msg[2]) > 0:
                    self.new_message.emit(msg[0], msg[2])
        # TODO: catch redis.exceptions.ConnectionError and retry

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, idle_icon, message_icon, parent=None):
        self.idle_icon = idle_icon
        self.message_icon = message_icon

        QtGui.QSystemTrayIcon.__init__(self, idle_icon, parent)

        self.setToolTip("Listening for irssi redis events on " \
                + config.redis['server'] + ":" + str(config.redis['port']))

        menu = QtGui.QMenu(parent)
        exitAction = menu.addAction("Exit").triggered.connect(self.onExit)
        self.setContextMenu(menu)

        self.activated.connect(self.onActivated)
        self.messageClicked.connect(self.onClear)

        self.listenThread = ListenThread()
        self.listenThread.new_message.connect(self.onNotify)
        self.listenThread.clear.connect(self.onClear)
        self.listenThread.start()

    def onActivated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            print "clearing because left click"
            self.onClear()

    def onClear(self):
        self.setIcon(self.idle_icon)

    def onNotify(self, channel, msg):
        # change tool tip?
        self.setIcon(self.message_icon)
        self.showMessage(channel, msg, QtGui.QSystemTrayIcon.NoIcon, MESSAGE_TIMEOUT)

    def onExit(self):
        print "exiting because menu"
        sys.exit(1)


def main():
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon(IDLE_ICON), QtGui.QIcon(MESSAGE_ICON), w)
    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
