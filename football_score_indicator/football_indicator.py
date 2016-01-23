#!/usr/bin/env python

from gi.repository import Gtk,GObject,GdkPixbuf
from gi.repository import AppIndicator3 as appindicator
from configuration import Configurations

from os import path
import threading
import time
import signal
import webbrowser

from espnfootball_scrap import get_matches_summary, get_match_goaldata
from Preferences import PreferencesWindow

ICON = path.abspath(path.dirname(__file__))+"/football.png"
VERSION_STR="0.1"
#time ot between each fetch
REFRESH_INTERVAL = 10

class FootballIndicator:
    def __init__(self):
        self.config = Configurations()
        self.indicator = appindicator.Indicator.new("football-score-indicator",
                        ICON,
                        appindicator.IndicatorCategory.APPLICATION_STATUS)
        # path.abspath(path.dirname(__file__))+"/football.png"
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_icon(ICON)

        self.indicatorLabelId = None
        self.indicator.set_label("No Live Matches","")

        self.menu = Gtk.Menu().new()
        self.indicator.set_menu(self.menu)

        self.matchMenu = []
        addQuitAboutPreferences(self.menu)

        self.dataLock = threading.Semaphore()

    def main(self):
        signal.signal(signal.SIGINT,signal.SIG_DFL)
        thread = threading.Thread(target = self.updateDataAfterInterval)
        #print thread.name
        thread.daemon = True
        thread.start()
        Gtk.main()

    def setIndicatorLabel(self,label):
        self.indicator.set_label(label,"Football Score Indicator")

    def insertMenuItem(self,widget,pos):
        self.menu.insert(widget,pos)

    def removeMenuItem(self,widget):
        self.menu.remove(widget)

    def showClicked_cb(self, widget, matchItem):
        self.indicatorLabelId = matchItem['id']
        #print "show clicked id is  :   ---   ",
        #print matchItem['id']

        # NOTE: `idle_add` is not required here as we are in callback and
        # therefore can modify Gtk data structures
        # NOTE: this function seems to be causing crash
        # take a good look at the args passed to it
        self.setIndicatorLabel(matchItem['gtkSummary'].get_label())

    def updateDataAfterInterval(self):
        while True:
            start = time.time()
            self.dataLock.acquire()
            self.updateLabels()
            self.setSubMenuData()
            self.dataLock.release()
            duration = time.time() - start
            if duration < REFRESH_INTERVAL:
                # sleep if time permits
                time.sleep(REFRESH_INTERVAL-duration)

    def updateLabels(self):
        # TODO: use caching
        settings = self.config.readConfigurations()
        #print settings

        leauges = get_matches_summary()
        if leauges is None:
            return

        currentCount = 0
        previousLength = len(self.menu) - 3
        for leauge,matches in leauges.iteritems():
            # TODO: use a creator function for creating Gtk objects
            newLeaugeItem = Gtk.MenuItem(leauge)
            newLeaugeItem.set_sensitive(False)
            if currentCount >= previousLength :
                GObject.idle_add(self.insertMenuItem,newLeaugeItem,currentCount)
                self.matchMenu.append(leauge)
            else:
                # %% we're using the old menuitem
                if self.menu.get_children()[currentCount].get_submenu():
                    # %% why r u doing dis?
                    GObject.idle_add(self.removeMenuItem,self.menu.get_children()[currentCount])
                    GObject.idle_add(self.insertMenuItem,newLeaugeItem,currentCount)
                else:
                    GObject.idle_add(setMenuLabel,self.menu.get_children()[currentCount],leauge)
                self.matchMenu[currentCount] = leauge
            if not settings['hide_leauges']:
                GObject.idle_add(newLeaugeItem.show)
            else:
                GObject.idle_add(newLeaugeItem.hide)
            currentCount += 1
            for matchInfo in matches.values():
                if self.indicatorLabelId is None:
                    self.indicatorLabelId = matchInfo['id']
                if self.indicatorLabelId == matchInfo['id']:
                    if ":" in matchInfo['status']:
                        GObject.idle_add(self.setIndicatorLabel,matchInfo['score_summary'] + " starts at " + matchInfo['status'])
                    else:
                        GObject.idle_add(self.setIndicatorLabel, matchInfo['score_summary'] + "  " + matchInfo['status'])

                if previousLength <= currentCount:
                    matchItem = self.createMatchItem(matchInfo)
                    if ":" in matchInfo['status']:
                        GObject.idle_add(setMenuLabel,matchItem['gtkSummary'],matchInfo['score_summary'] + " Starts at " + matchInfo['status'])
                    else:
                        GObject.idle_add(setMenuLabel,matchItem['gtkSummary'],matchInfo['score_summary'] + "\n " + matchInfo['status'])
                    self.matchMenu.append(matchItem)
                    GObject.idle_add(self.insertMenuItem,matchItem['gtkSummary'],currentCount)
                    GObject.idle_add(matchItem['gtkSummary'].show)
                else:
                    widget = self.menu.get_children()[currentCount]
                    if type(self.matchMenu[currentCount]) is dict:
                        self.updateMenu(self.matchMenu[currentCount],matchInfo)
                    else:
                        widget.set_sensitive(True)
                        matchItem = self.createMatchItem(matchInfo,widget)
                        if ":" in matchInfo['status']:
                            GObject.idle_add(setMenuLabel,matchItem['gtkSummary'],matchInfo['score_summary'] + " Starts at " + matchInfo['status'])
                        else:
                            GObject.idle_add(setMenuLabel,matchItem['gtkSummary'],matchInfo['score_summary'] + "\n " + matchInfo['status'])
                        self.matchMenu[currentCount] = matchItem

                if settings['live_matches'] and 'LIVE' in self.matchMenu[currentCount]['status']:
                    GObject.idle_add(self.matchMenu[currentCount]['gtkSummary'].show)
                elif not settings['live_matches']:
                    GObject.idle_add(self.matchMenu[currentCount]['gtkSummary'].show)
                else:
                    GObject.idle_add(self.matchMenu[currentCount]['gtkSummary'].hide)
                currentCount += 1

        """
        check this pattter
        """
        while currentCount < len(self.menu) - 3:
            print "in while loop"
            print "currentCount ----------------------------------------------> ", currentCount
            print "sen(self.menu) --------------------------------------------> ",len(self.menu)
            print "match menu length -----------------------------------------> ", len(self.matchMenu)
            GObject.idle_add(self.removeMenuItem, self.menu.get_children()[currentCount + 1])
            #if type(self.matchMenu[-1]) is dict:
            #  GObject.idle_add(self.removeMenuItem, self.menu.get_children()[-4])
            #else:
            #  GObject.idle_add(self.removeMenuItem,self.matchMenu[-1])

    def createMatchItem(self,matchInfo, widget = None):
        matchItem = {
          "gtkSummary":       Gtk.ImageMenuItem.new_with_label(matchInfo['score_summary'] + "\t\t\t" + matchInfo['status'])
                              if widget is None else widget,
          "gtkSubMenu":       Gtk.Menu.new(),
          "gtkSetAslabel":    Gtk.MenuItem("Set as Label"),
          "gtkOpenInBrowser": Gtk.MenuItem.new_with_label("Open in Browser"),
          "gtkSeperator1":    Gtk.SeparatorMenuItem().new(),
          "gtkSeperator2":    Gtk.SeparatorMenuItem().new(),
          "gtkSeperator3":    Gtk.SeparatorMenuItem().new(),

          "gtkGoalHeading":       Gtk.MenuItem("Goals"),
          "gtkGoalData":          Gtk.MenuItem("Loading..."),
          "gtkStatus":            Gtk.MenuItem("Loading..."),
          "gtkSubMenuScoreLabel": Gtk.MenuItem("Loading"),

          "id":        matchInfo["id"],
          "leauge":    matchInfo["leauge"],
          "status":    matchInfo['status'],
          "extraInfo": matchInfo['extra_info'],
          "url":       matchInfo['url'],

        }
        matchItem['gtkSummary'].set_submenu(matchItem['gtkSubMenu'])

        matchItem['gtkSetAslabel'].connect("activate",self.showClicked_cb,matchItem)
        matchItem['gtkOpenInBrowser'].connect("activate",self.openInBrowser_cb,matchItem)

        matchItem['gtkSubMenu'].append(matchItem['gtkSetAslabel'])
        matchItem['gtkSubMenu'].append(matchItem['gtkSeperator1'])
        matchItem['gtkSubMenu'].append(matchItem['gtkSubMenuScoreLabel'])
        matchItem['gtkSubMenu'].append(matchItem['gtkStatus'])
        matchItem['gtkSubMenu'].append(matchItem['gtkSeperator2'])
        matchItem['gtkSubMenu'].append(matchItem['gtkGoalHeading'])
        matchItem['gtkSubMenu'].append(matchItem['gtkGoalData'])
        matchItem['gtkSubMenu'].append(matchItem['gtkSeperator3'])
        matchItem['gtkSubMenu'].append(matchItem['gtkOpenInBrowser'])

        matchItem['gtkSubMenu'].show_all()
        # matchItem['gtkOpenInBrowser'].show()
        # matchItem['gtkSummary'].show()
        # matchItem['gtkSetAslabel'].show()
        # matchItem['gtkSeperator1'].show()
        # matchItem['gtkSeperator2'].show()
        # matchItem['gtkSeperator3'].show()
        # matchItem['gtkGoalHeading'].show()
        # matchItem['gtkGoalData'].show()
        # matchItem['gtkSubMenuScoreLabel'].show()
        # matchItem['gtkStatus'].show()

        return matchItem

    def openInBrowser_cb(self,widget,matchItem):
        webbrowser.open(matchItem['url'])


    def updateMenu(self,widget,matchInfo):
        #print widget.keys()
        if ":" in matchInfo['status']:
            #widget['gtkSummary'].set_label(matchInfo['score_summary'] + " starts at " + matchInfo['status'])
            GObject.idle_add(widget['gtkSummary'].set_label,matchInfo['score_summary'] + " starts at " + matchInfo['status'])
        else:
            #widget['gtkSummary'].set_label(matchInfo['score_summary'] + "  " + matchInfo['status'])
            GObject.idle_add(widget['gtkSummary'].set_label,matchInfo['score_summary'] + " " + matchInfo['status'])
            #print widget['gtkSummary'].get_label()
            #print 'LIVE' in matchInfo['status']



            if 'LIVE' in matchInfo['status']:
                image = Gtk.Image()
                image.set_from_file(path.abspath(path.dirname(__file__))+"/football.png")
                #widget['gtkSummary'].set_image(image)
                GObject.idle_add(widget['gtkSummary'].set_image,image)
                widget['gtkSummary'].set_always_show_image(True)
                print "---------------------------------it is live image has beed set"
            else:
                widget['gtkSummary'].set_always_show_image(False)






        #widget['gtkSubMenuScoreLabel'].set_label(matchInfo['score_summary'])
        GObject.idle_add(setMenuLabel,widget['gtkSubMenuScoreLabel'],matchInfo['score_summary'] )

        #widget['gtkStatus'].set_label(matchInfo['status'])
        GObject.idle_add(setMenuLabel,widget['gtkStatus'],matchInfo['status'])
        widget['gtkStatus'].set_sensitive(False)

        #widget['gtkSetAslabel'].set_label("Set as Label ")

        GObject.idle_add(setMenuLabel,widget['gtkSetAslabel'],"Set as Label")



        #print widget['gtkSummary'].get_label()
        widget['id'] = matchInfo['id']
        widget['status'] = matchInfo['status']
        #print matchInfo['status']
        #print matchInfo['status']
        widget['extraInfo'] = matchInfo['extra_info']
        #print matchInfo['extra_info']
        widget['url'] = matchInfo['url']
        widget['leauge'] = matchInfo['leauge']
        #print ("matchitem is dictionary updated")
        #leading to blocking of main and gtk target-action pattter thread.join()

    def updateSubMenuLabels(self,matchId,widget):
        goals = get_match_goaldata(matchId)
        if not goals:
            #print "goals are not available"
            #widget.set_label("No Goals Yet")
            GObject.idle_add(widget.set_label,"No Goals Yet...")
            return
        else:
            print "goals available"
            str = ""
            for i in goals:
                str += i.replace("<b>","").replace("</b>","").replace("<br>","") + "\n"
                #print str
            #widget.set_label(str)
            GObject.idle_add(widget.set_label, str)

    def setSubMenuData(self):
        print "going in to setSubmenuData"

        for i in self.matchMenu:
            if type(i) is dict and 'LIVE' in i['gtkStatus'].get_label():
                thread = threading.Thread(target=self.updateSubMenuLabels,args=(i['id'], i['gtkGoalData']))
                thread.start()

def run():
    myIndicator = FootballIndicator()
    myIndicator.main()

if __name__ == "__main__":
    print ("use 'footnallscore_indicator to run the applet")

# TODO: move to scraper file

def setMenuLabel(widget, label):
    widget.set_label(label)

def preferences(widget):
    window = PreferencesWindow()
    window.display()

def about(widget):
    dialog = Gtk.AboutDialog.new()
    dialog.set_transient_for(widget.get_parent().get_parent())

    dialog.set_program_name("Football Score Indicator")
    dialog.set_authors(["Nishant Kukreja", "Abhishek"])
    dialog.set_license_type(Gtk.License.GPL_3_0)
    dialog.set_version(VERSION_STR)

    dialog.run()
    dialog.destroy()

def quit(widget):
    print "*** quit clicked ***"
    Gtk.main_quit()

def addQuitAboutPreferences(menu):
    preferences_item = Gtk.MenuItem('Preferences')
    preferences_item.connect("activate", preferences)
    preferences_item.show()

    about_item = Gtk.MenuItem("About")
    about_item.connect("activate", about)
    about_item.show()

    quit_item = Gtk.MenuItem("Quit")
    quit_item.connect("activate", quit)
    quit_item.show()

    menu.append(preferences_item)
    menu.append(about_item)
    menu.append(quit_item)


# vim: ts=2
