#!/usr/bin/env python
import sys
import redis
import time
from PyQt4 import QtGui
from PyQt4.QtCore import *

# local config file
import config

# TODO: better icons (these were lifted from KDE4 Oxygen theme)
IDLE_ICON="idle.png"
MESSAGE_ICON="message.png"
ERROR_ICON="error.png"

# how long to show the message bubble
MESSAGE_TIMEOUT=2000 # ms
RECONNECT_DELAY=10000 # ms

def servername():
    return config.redis['server'] + ":" + str(config.redis['port'])

class ListenThread(QThread):
    new_message = pyqtSignal(str,str,name='newMessage')
    clear       = pyqtSignal(name='clear')
    error       = pyqtSignal(name='error')

    def __init__(self):
        QThread.__init__(self)

    def listen(self):
        print "connecting to redis at", servername()
        r = redis.StrictRedis(
                host=config.redis['server'],
                port=config.redis['port'],
                password=config.redis['password'],
                db=0
            )
        ps = r.pubsub()
        ps.subscribe(['irssi'])

        self.clear.emit() # clear any error state due to successful conn

        for item in ps.listen():
            print item
            msg = str(item['data']).partition('  ')
            if item['type'] == 'message':
                if msg[0] == '__CLEAR__':
                    # my irssi script sends this special __CLEAR__ code
                    # when there's a keypress in irssi since last message posted
                    self.clear.emit()
                elif len(msg[2]) > 0:
                    self.new_message.emit(msg[0], msg[2])

    def run(self):
        while True:
            try:
                self.listen()
            except redis.exceptions.ConnectionError, e:
                print "Caught exception:", e
                self.error.emit()
                print "Waiting for a bit and trying again"
                time.sleep(RECONNECT_DELAY * 1000.0)


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, idle_icon, message_icon, error_icon, parent=None):
        self.notifications = 0

        self.idle_icon = idle_icon
        self.message_icon = message_icon
        self.error_icon = error_icon

        QtGui.QSystemTrayIcon.__init__(self, idle_icon, parent)

        menu = QtGui.QMenu(parent)
        exitAction = menu.addAction("Exit").triggered.connect(self.onExit)
        self.setContextMenu(menu)

        self.activated.connect(self.onActivated)
        self.messageClicked.connect(self.onClear)

        self.listenThread = ListenThread()
        self.listenThread.new_message.connect(self.onNotify)
        self.listenThread.clear.connect(self.onClear)
        self.listenThread.error.connect(self.onError)
        self.listenThread.start()

    def onActivated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.onClear()

    def onError(self):
        self.setToolTip("Error connectiong to " + servername())
        self.setIcon(self.error_icon)

    def onClear(self):
        self.notifications = 0
        self.setToolTip("Listening for irssi redis events on " \
                + config.redis['server'] + ":" + str(config.redis['port']))
        self.setIcon(self.idle_icon)

    def onNotify(self, channel, msg):
        self.notifications += 1
        if self.notifications == 1:
            self.setToolTip("New event from " + servername())
        else:
            self.setToolTip("%d new events from %s" % (self.notifications, servername()))
        self.setIcon(self.message_icon)
        self.showMessage(channel, msg, QtGui.QSystemTrayIcon.NoIcon, MESSAGE_TIMEOUT)

    def onExit(self):
        sys.exit(1)


def main():
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    trayIcon = SystemTrayIcon(
            QtGui.QIcon(IDLE_ICON),
            QtGui.QIcon(MESSAGE_ICON),
            QtGui.QIcon(ERROR_ICON),
            w)
    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
