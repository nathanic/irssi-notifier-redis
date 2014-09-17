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
MESSAGE_TIMEOUT=4 * 1000 # msec
RECONNECT_DELAY=10.0     # sec

def servername():
    return config.redis['server'] + ":" + str(config.redis['port'])

class ListenThread(QThread):
    # how to make a signal take a list of strings?
    # new_message = pyqtSignal(str,str,name='newMessage')
    new_message = pyqtSignal(list,name='newMessage')
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
            if item['type'] == 'message':
                parts = str(item['data']).split("\t", 3)
                if parts[0] == 'CLEAR':
                    self.clear.emit()
                elif len(parts) == 4:
                    self.new_message.emit(parts)
                else:
                    print "malformed message: ", parts

    def run(self):
        while True:
            try:
                self.listen()
            except redis.exceptions.ConnectionError, e:
                print "Caught exception:", e
                self.error.emit()
                print "Waiting for a bit and trying again"
                time.sleep(RECONNECT_DELAY)


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, idle_icon, message_icon, error_icon, parent=None):
        self.notifications = []
        self.error = True

        self.idle_icon = idle_icon
        self.message_icon = message_icon
        self.error_icon = error_icon

        QtGui.QSystemTrayIcon.__init__(self, error_icon, parent)

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
            if not self.error:
                self.onClear()

    def onError(self):
        self.setToolTip("Error connectiong to " + servername())
        self.setIcon(self.error_icon)
        self.error = True

    def onClear(self):
        self.notifications = []
        self.error = False
        self.setToolTip("Listening for irssi redis events on " \
                + config.redis['server'] + ":" + str(config.redis['port']))
        self.setIcon(self.idle_icon)

    def onNotify(self, parts):
        cmd, network, channel, msg = parts
        # might want to change the protocol to send
        # cmd\tnick\tmsg
        self.notifications.append( parts )
        if len(self.notifications) == 1:
            events = "New event"
        else:
            events = "%d new events" % len(self.notifications)
        chans = list( set( (notifo[2] for notifo in self.notifications) ) )
        if len(chans) == 1:
            chans = chans[0]
        self.setToolTip("%s from %s on %s" % (events, chans, servername()))
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
