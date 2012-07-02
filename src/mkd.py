#!/usr/bin/env python2

'''
Created on 11.03.2010

@author: Arthur Spitzer <arthapex@gmail.com>
'''

import dbus.mainloop.glib
import dbus.service

import gobject

from optparse import OptionParser
import time


AppName = 'mediakeys-daemon'
Version='0.2'

DbusBusName = 'org.gnome.SettingsDaemon'
DbusObjectPath = '/org/gnome/SettingsDaemon/MediaKeys'
DbusInterface = 'org.gnome.SettingsDaemon.MediaKeys'



class App(object):
    def __init__(self, app_name, app_time):
        self.name = app_name
        self.time = int(app_time)

    def __cmp__(self, other):
        return self.time.__cmp__(other.time)



class SettingsDaemonObject(dbus.service.Object):
    def __init__(self, session_bus):
        dbus.service.Object.__init__(self, session_bus, object_path=DbusObjectPath)
        self.__paused = False
        self.__playing = False
        self.__apps = []

    def __find_app(self, app_name):
        for app in self.__apps:
            if app.name == app_name:
                return app
        return None

    @dbus.service.method(dbus_interface=DbusInterface, in_signature='sd', out_signature='')
    def GrabMediaPlayerKeys(self, app_name, app_time):
        # Each app registers with a timestamp (priority). The app with the
        # most recent timestamp (highest priority) gets the notification.
        # Timestamp may be 0 for the current time. 1 is commonly used for
        # "least priority" (e.g. by Evince). Timestamps are in milliseconds.
        if app_time == 0:
            app_time = int(time.time()*1000)
        # Check if app is already registered; update timestamp if so.
        app = self.__find_app(app_name)
        if app:
            if app.time < app_time:
                self.__apps.remove(app)
            else:
                return
        # Install new app into the list
        self.__apps.append(App(app_name, app_time))
        self.__apps.sort(reverse=True)
    
    @dbus.service.method(dbus_interface=DbusInterface, in_signature='s', out_signature='')
    def ReleaseMediaPlayerKeys(self, app_name):
        app = self.__find_app(app_name)
        if app:
            self.__apps.remove(app)

    @dbus.service.signal(dbus_interface=DbusInterface)
    def MediaPlayerKeyPressed(self, app_name, action):
        pass
    
    def __send_action_to_app(self, action):
        # Send media key notification to highest-priority application.
        if len(self.__apps):
            app = self.__apps[0]
            self.MediaPlayerKeyPressed(app.name, action)
    
    @dbus.service.method(dbus_interface=DbusInterface)
    def PressedPlay(self):
        self.__send_action_to_app('Play')
        self.__playing = True
    
    @dbus.service.method(dbus_interface=DbusInterface)
    def PressedPause(self):
        self.__send_action_to_app('Pause')
    
    @dbus.service.method(dbus_interface=DbusInterface)
    def PressedStop(self):
        self.__send_action_to_app('Stop')
    
    @dbus.service.method(dbus_interface=DbusInterface)
    def PressedNext(self):
        self.__send_action_to_app('Next')
    
    @dbus.service.method(dbus_interface=DbusInterface)
    def PressedPrevious(self):
        self.__send_action_to_app('Previous')
    


class Server(object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        session_bus = dbus.SessionBus()
        activeServices = session_bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').ListNames()

        if not DbusBusName in activeServices:
            name = dbus.service.BusName(DbusBusName, session_bus)
            object = SettingsDaemonObject(session_bus)

            mainloop = gobject.MainLoop()
            mainloop.run()
        else:
            print "Service for interface %s is already running." % DbusBusName



class Client(object): 
    def __init__(self):
        service = dbus.SessionBus().get_object(DbusBusName, DbusObjectPath)
        self.__dbusInterface = dbus.Interface(service, DbusInterface)

    def play(self):
        self.__dbusInterface.PressedPlay()
    
    def pause(self):
        self.__dbusInterface.PressedPause()
    
    def stop(self):
        self.__dbusInterface.PressedStop()
    
    def next(self):
        self.__dbusInterface.PressedNext()
    
    def previous(self):
        self.__dbusInterface.PressedPrevious()



if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog [options] ', version=Version,
                          description="Multimedia Key Daemon")  
    parser.add_option('-p', '--play', action='store_true',
                      help='send play event to all listeners',
                      dest='play', default=False)
    parser.add_option('-a', '--pause', action='store_true',
                      help='send pause event to all listeners',
                      dest='pause', default=False)
    parser.add_option('-s', '--stop', action='store_true',
                      help='send stop event to all listeners',
                      dest='stop', default=False)
    parser.add_option('-n', '--next', action='store_true',
                      help='send next-track event to all listeners',
                      dest='next', default=False)
    parser.add_option('-b', '--previous', action='store_true',
                      help='send previous-track event to all listeners',
                      dest='previous', default=False)
    parser.add_option('-d', '--daemon', action='store_true',
                      help='start the daemon, if not already running',
                      dest='daemon', default=False)
    (options, args) = parser.parse_args()
   
    if args=="none":
        parser.print_help()
    
    if options.daemon:
        d = Server()
    else:
        if options.play:
            client = Client()
            client.play()
        elif options.pause:
            client = Client()
            client.pause()
        elif options.stop:
            client = Client()
            client.stop()
        elif options.next:
            client = Client()
            client.next()
        elif options.previous:
            client = Client()
            client.previous()
        else:
            parser.print_help()

