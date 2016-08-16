#!usr/bin/env python

import sys
import json
import gi.repository

from gi.repository import Gtk,GObject,Gdk,GtkSource
from gi.repository import Pango
from gi.repository import AppIndicator3 as appindicator
from configuration import Configurations


from os.path import expanduser
import glob
import os

""" we will remove it later"""
import ConfigParser
import re

""" yet learning login """
import logging
logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)


home = expanduser('~')

class PreferencesWindow:

    def __init__(self):
        logger.debug("Initializing PREFERENCES Object")
        self.builder = Gtk.Builder()
        d = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        #print d
        d = os.path.join(d,"Preferences.glade")
        #print d
        self.builder.add_from_file(d)
        self.preferences_window = self.builder.get_object("preferences_window")
        self.button1 = self.builder.get_object('radiobutton1')
        self.button2 = self.builder.get_object('radiobutton2')
        self.button3 = self.builder.get_object('checkbutton1')
        self.preferences_window.set_can_focus(True)
        self.preferences_window.connect('delete_event',self.hide)

        self.button1.connect('toggled',self.on_button_toggled,'1')
        self.button2.connect('toggled',self.on_button_toggled,'2')
        self.button3.connect('toggled',self.on_button_toggled,'3')



    def hide(self,widget,event):
        GObject.idle_add(self.preferences_window.hide)
        return True

    def readConfigurations(self):
    	logger.debug("READING Configurations")
        self.config = Configurations().readConfigurations()

    def setConfigurations(self):
    	logger.debug("SETTING Configurations")
        self.button1.set_active(self.config['live_matches'])
        self.button2.set_active(self.config['all_matches'])
        self.button3.set_active(self.config['hide_leauges'])
 
    def on_button_toggled(self, button, name):
    	logger.debug("Button toggled")
        if button.get_active():
            state = "on"
        else:
            state = "off"
        print("Button", name, "was turned", state)

        self.config['all_matches'] = self.button2.get_active()
        self.config['live_matches'] = self.button1.get_active()
        self.config['hide_leauges'] = self.button3.get_active()

        Configurations().writeConfigurations(self.config)
        self.callback()



    def display(self,func):
    	logger.debug(" In DISPLAY Function")
        self.readConfigurations()
        GObject.idle_add(self.setConfigurations)
        self.callback = func
        GObject.idle_add(self.preferences_window.grab_focus)


        GObject.idle_add(self.preferences_window.show_all)
    


