Irssi Notifier Using Redis and PyQt4
====================================
*Running irssi on a remote server and want to receive notifications on your local computer?*

This irssi notifier uses Redis to connect your local computer to your remote
irssi. Notifications will be displayed using a system tray icon.  If you click
the tray icon, or even enter a keypress in irssi, the notification state will
be cleared out.

Install
=======

Irssi server
------------
* Install Redis server: http://redis.io/download
* Install Redis with cpan: http://search.cpan.org/~melo/Redis-1.955/lib/Redis.pm
* Place notify_redis.pl in ~/.irssi/scripts/autorun
* Edit notify_redis.pl to configure your Redis server
* Start irssi and type;
<pre>
/load perl
/script load autorun/notify_redis.pl
</pre>

Local client
-------------
* Install redis-py: https://github.com/andymccurdy/redis-py
* Copy config.dist.py to config.py and enter the correct settings
* Start listen_redis.py
* Enjoy!

Security
========
Don't forget to secure your server and enable the requirepass option in your redis.conf.


