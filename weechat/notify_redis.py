# -*- coding: utf-8 -*-
# Author: Caspar Clemens Mierau <ccm@screenage.de>
# Homepage: https://github.com/leitmedium/weechat-irssinotifier
# Derived from: notifo
#   Author: ochameau <poirot.alex AT gmail DOT com>
#   Homepage: https://github.com/ochameau/weechat-notifo
# And from: notify
#   Author: lavaramano <lavaramano AT gmail DOT com>
#   Improved by: BaSh - <bash.lnx AT gmail DOT com>
#   Ported to Weechat 0.3.0 by: Sharn - <sharntehnub AT gmail DOT com)
# And from: notifo_notify
#   Author: SAEKI Yoshiyasu <laclef_yoshiyasu@yahoo.co.jp>
#   Homepage: http://bitbucket.org/laclefyoshi/weechat/
#
# This plugin brings IrssiNotifier to your Weechat. Setup and install
# IrssiNotifier first: https://irssinotifier.appspot.com
#
# Requires Weechat >= 0.3.7, openssl
# Released under GNU GPL v3
#
# 2014-05-10, Sébastien Helleu <flashcode@flashtux.org>
#     version 0.6: - change hook_print callback argument type of
#                    displayed/highlight (WeeChat >= 1.0)
# 2013-01-18, ccm <ccm@screenage.de>:
#     version 0.5: - removed version check and legacy curl usage
# 2012-12-27, ccm <ccm@screenage.de>:
#     version 0.4: - use non-blocking hook_process_hashtable for url call
#                    for weechat >= 0.3.7
# 2012-12-22, ccm <ccm@screenage.de>:
#     version 0.3: - no longer notifies if the message comes from the user
#                    itself
#                  - removed curl dependency
#                  - cleaned up openssl call
#                  - no more crashes due to missing escaping
#                  - Kudos to Juergen "@tante" Geuter <tante@the-gay-bar.com>
#                    for the patches!
# 2012-10-27, ccm <ccm@screenage.de>:
#     version 0.2: - curl uses secure command call (decreases risk of command
#                    injection)
#                  - correct split of nick and channel name in a hilight
# 2012-10-26, ccm <ccm@screenage.de>:
#     version 0.1: - initial release - working proof of concept

import weechat, string, os

try:
    import redis
except:
    weechat.prnt("", "You need to install the python redis library.")


weechat.register("notify_redis", "Nathan P. Stien <nathanism@gmail.com", "0.1", "GPL3", "notify_redis: Send notification messages to a redis pubsub topic.", "", "")

# config values: redis hostname, redis port, redis topic
settings = {
        "redis_hostname": "localhost",
        "redis_port": 6379,
        "redis_topic": 'irssi'
}

# for option, default_value in settings.items():
#     if weechat.config_get_plugin(option) == "":
#         weechat.prnt("", weechat.prefix("error") + "irssinotifier: Please set option: %s" % option)
#         weechat.prnt("", "irssinotifier: /set plugins.var.python.irssinotifier.%s STRING" % option)

# Hook privmsg/hilights
weechat.hook_print("", "irc_privmsg", "", 1, "notify_show", "")
weechat.hook_signal("key_pressed","on_key_pressed", "")

need_to_clear = False

def on_key_pressed(a, b, c):
    global need_to_clear
    if need_to_clear:
        notify_clear()
        need_to_clear = False
    return weechat.WEECHAT_RC_OK


# Functions
def notify_show(data, bufferp, uber_empty, tagsn, isdisplayed,
        ishilight, prefix, message):

    #get local nick for buffer
    mynick = weechat.buffer_get_string(bufferp,"localvar_nick")

    # only notify if the message was not sent by myself
    if (weechat.buffer_get_string(bufferp, "localvar_type") == "private") and (prefix!=mynick):
        publish_notification(prefix, prefix, message)
    elif int(ishilight):
        buffer = (weechat.buffer_get_string(bufferp, "short_name") or
                weechat.buffer_get_string(bufferp, "name"))
        publish_notification(buffer, prefix, message)

    return weechat.WEECHAT_RC_OK

def notify_clear():
    r = redis.StrictRedis(host="localhost", port=6379, password=None, db=0)
    r.publish('irssi', 'CLEAR')


def publish_notification(chan, nick, message):
    r = redis.StrictRedis(host="localhost", port=6379, password=None, db=0)
    # ps = r.pubsub()
    # $stripped =~ s/[^a-zA-Z0-9 .,!?\@:\/\>\=]//g;
    r.publish('irssi', 'HIGHLIGHT\t<server>\t%s\t%s' % (chan, message))
    global need_to_clear
    need_to_clear = True


# vim: autoindent expandtab smarttab shiftwidth=4
