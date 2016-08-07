mediakeys-daemon
================

Python implementation of Gnome's org.gnome.SettingsDaemon.MediaKeys, for use on other desktop environments.
It has the additional possibility to execute commands on this interface.

This makes it possible to bind the mediakeys on your keyboard with the corresponding actions on the interface, and thus control every running media-player.

Options:
-------------------
```  
  --version       show program's version number and exit
  -h, --help      show this help message and exit
  -p, --play      send play event to all listeners
  -a, --pause     send pause event to all listeners
  -s, --stop      send stop event to all listeners
  -n, --next      send next-track event to all listeners
  -b, --previous  send previous-track event to all listeners
  -d, --daemon    start the daemon, if not already running
```


Programs supporting the interface
----------------
    Rhythmbox
    Decibel Audio Player
    Banshee
    Totem
    gnome-mplayer
    Sonata
    Gnome Music Player Client (gmpc)
    Vagalume
    Ballroom Audio Player
    Evince
    ... probably some more

Besides it's functionality, the mkd.py-file can be used as an example in creating single instance-applications using dbus.

I forked it from the [original version by arthapex](https://gitorious.org/mediakeys-daemon) to fix some bugs.

It is available under the GNU General Public License, version 2 (GPLv2).
