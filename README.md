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
* Install Redis Perl libs with cpan: http://search.cpan.org/~melo/Redis-1.955/lib/Redis.pm
* OR install Redis Perl libs on Debian/Ubuntu with: `sudo apt-get install libredis-perl`
* Place notify_redis.pl in `~/.irssi/scripts/autorun`
* Edit notify_redis.pl to configure your Redis server
* Start irssi and type;
<pre>
/load perl
/script load autorun/notify_redis.pl
</pre>

Local client
-------------
* Install redis-py: https://github.com/andymccurdy/redis-py
* Or install it on Debian/Ubuntu: `sudo apt-get install python-redis`
* Copy config.dist.py to config.py and enter the correct settings
* Start listen_redis.py
* Enjoy!

If your notification client is on a different machine/network from your irssi instance, you should probably use an ssh tunnel to securely reach Redis.  I do something like this, which will forward traffic from the client machine's port 16379 to the Redis port (6379) on the remote server:

    ssh -L16379:localhost:6379 <server-address>

And then I configure the client to connect to localhost:16379.

In fact, I usually use [`autossh`](http://www.harding.motd.ca/autossh/) and [set up an ssh keypair](https://help.ubuntu.com/community/SSH/OpenSSH/Keys) so that the tunnel can be automatically restored if it goes down.

Secuity
========
Don't forget to secure your server and enable the requirepass option in your redis.conf.


