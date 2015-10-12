#!/usr/bin/env python

from gi.repository import Gtk, GObject, GdkPixbuf
from gi.repository import AppIndicator3 as appindicator

from os import path
import threading
import time
import signal
import sys

# the timeout between each fetch
REFRESH_INTERVAL = 10 # second(s)
ICON_PATH = path.join(path.abspath(path.dirname(__file__)), "icons/")

class scores_ind:
    def __init__(self):
        """
        Initialize appindicator and other menus
        """

        self.indicator = appindicator.Indicator.new("football-scores-indicator",
                                                ICON_PATH + "0.png",
                                                appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.menu = self.menu_setup()
        self.indicator.set_menu(self.menu)


    def main(self):
        # handle 'C-c'
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()

    def menu_setup(self):
        """
        Setup the Gtk menu of the indicator
        """

        menu = Gtk.Menu.new()

        # some self promotion
        about_item = Gtk.MenuItem("About")
        about_item.connect("activate",self.about)
        about_item.show()

        menu.append(about_item)

        #we need a way to quit if the indicator is irritating ;)
        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.quit)
        quit_item.show()

        menu.append(quit_item)

        return menu


    def quit(self, widget):
        Gtk.main_quit()

    def about(self, widget):
    	dialog = Gtk.AboutDialog.new()
    	# fixes the "mapped without transient parent" warning
    	dialog.set_transient_for(widget.get_parent().get_parent())

    	dialog.set_program_name("Football Score Indicator")
    	dialog.add_credit_section("Authors:", ['Nishant Kukreja (github.com/rubyace71697)', 'Abhishek (github.com/rawcoder)'])
    	dialog.set_license_type(Gtk.License.GPL_3_0)
    	#dialog.set_website("https://github.com/rubyAce71697/cricket-score-applet")
    	#dialog.set_website_label("Github page")
    	#dialog.set_comments("Displays live football scores in your indicator panel")
    	#dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(ICON_PATH + "footballscores_indicator" + ".svg"))

    	dialog.run()
    	dialog.destroy()

    def add_menu(self, widget, pos):
        self.menu.insert(widget, pos)

    def remove_menu(self, widget):
        self.menu.remove(widget)

    def set_menu_label(self, widget, label):
        widget.set_label(label)

def run():
    myIndicator = scores_ind()
    myIndicator.main()

if __name__ == "__main__":
    print ("Use 'footballscore_indicator' to run the applet")
