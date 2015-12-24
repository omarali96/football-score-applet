#!/usr/bin/env python

from gi.repository import Gtk, GObject, GdkPixbuf
from gi.repository import AppIndicator3 as appindicator

from os import path
import threading
import time
import signal
import sys
import webbrowser
from espnfootball_scrap import ESPNFootballScrap
# the timeout between each fetch
REFRESH_INTERVAL = 10 #econd(s)
ICON_PATH = path.join(path.abspath(path.dirname(__file__)), "icons/")

class scores_ind:
    def __init__(self):
        """
        Initialize appindicator and other menus
        """

        self.indicator = appindicator.Indicator.new("football-scores-indicator",
                                                ICON_PATH + "23.png",
                                                appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.scrapObject =ESPNFootballScrap()
        self.indicatorLabelId = None
        self.indicator.set_label("Loading","")
        self.menu = Gtk.Menu().new()
        #self.listofGtkItems = []
        self.indicator.set_menu(self.menu)
        self.matchMenu = []
        self.addQuitAbout()
        #self.updateLabels()
        while Gtk.events_pending():
        		Gtk.main_iteration()
        thread = threading.Thread(target=self.updateData)
        thread.daemon = True
        thread.start()
        

    def main(self):
        # handle 'C-c'
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()

    def menu_setup(self):
        """
        Setup the Gtk menu of the indicator
        """

        self.matchMenu = []

        matches = self.scrapObject.get_matches_summary()
        #print "======================"
        #print (matches)
        #menu = Gtk.Menu.new()

        
        leagues = self.scrapObject.get_matches_summary()
        #print (len(self.menu))
        for i in self.menu.get_children():
        	self.menu.remove(i)
        for league in leagues:
        	self.matchMenu.append(league)
        	gtkLeagueItem = Gtk.MenuItem(league)
        	gtkLeagueItem.set_sensitive(False)
        	gtkLeagueItem.show()
        	#print ("second here")
        	self.menu.append(gtkLeagueItem)
        	#self.listofGtkItems.append(gtkLeagueItem)
        	for matches in leagues[league]:
        		matchInfo = leagues[league][matches]
        		#print (matchInfo)
        		#print ("====="*40)
	        	matchItem = self.createMatchItem(matchInfo)
	        	self.matchMenu.append(matchItem)
       	        self.menu.append(matchItem['gtkSummary'])
       	        #self.listofGtkItems.append(matchItem['gtkSummary'])
       	        #print (matchItem['gtkSummary'])
       	        matchItem['gtkSummary'].show()
       	        
       	        if self.indicatorLabelId is None:
       	        	self.indicatorLabelId = matchItem['id']

        # some self promotion
        about_item = Gtk.MenuItem("About")
        about_item.connect("activate",self.about)
        about_item.show()

        self.menu.append(about_item)

        #we need a way to quit if the indicator is irritating ;)
        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.quit)
        quit_item.show()

        self.menu.append(quit_item)
        print len(self.menu)
        #return menu
		

    def quit(self, widget):
        Gtk.main_quit()

    def addQuitAbout(self):
    	about_item = Gtk.MenuItem("About")
        about_item.connect("activate",self.about)
        about_item.show()

        self.menu.append(about_item)

        #we need a way to quit if the indicator is irritating ;)
        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.quit)
        quit_item.show()

        self.menu.append(quit_item)


    def updateLabels(self):

    	print "----------------------------***************************-------------------------------------------"
    	print "\n\n\n\n"

        leagues = self.scrapObject.get_matches_summary()
    	previousLength = len(self.menu)-2
    	print (previousLength)
    	for i in self.menu:
    		print (i).get_label()
    	print "\n\n"
    	print "-"*40
    	print "\n"
    	print
    	currentCount = 0
    	for league in leagues:
        	print ("current count : " ,currentCount)
        	print ("previousLength: ",previousLength)

        	if(previousLength <= currentCount):

        		print ("in league previous length is leass than current count therefore insert league")
        		
        		newGtkItem = Gtk.MenuItem(league + "inserted   " + str(currentCount))
        		self.menu.insert(newGtkItem,currentCount )
        		newGtkItem.show()
        		newGtkItem.set_sensitive(False)
        		while Gtk.events_pending():
        			Gtk.main_iteration()
        		print ("insert : " , league , (currentCount+1))
        
        		#self.listofGtkItems.append(newGtkItem)
        		self.matchMenu.append(league )
        		currentCount += 1

        	else:
        		print ("previous lenth is greatet thab the current count therefore we update")
        		self.menu.get_children()[currentCount].set_label(league + "updated   "  + str(currentCount))
        		print ("updated : " + league , (currentCount))
        		#self.listofGtkItems[currentCount].set_label(league)
        		self.matchMenu[currentCount] = league
        		currentCount +=1

        	for matches in leagues[league]:
        		matchInfo = leagues[league][matches]
        		print ("in match update")
        		print ("current count : " ,currentCount)
        		print("previousLength : ", previousLength)
        		if (previousLength <= currentCount):
        			matchItem = self.createMatchItem(matchInfo)
        			self.matchMenu.append(matchItem)

        			print ("inserting : ", matchItem['gtkSummary'].get_label(), currentCount+1)
        			self.menu.insert(matchItem['gtkSummary'] ,currentCount)
        			#self.listofGtkItems.append(matchItem['gtkSummary'])
        			matchItem['gtkSummary'].show()
        		else:
        			matchItem = self.createMatchItem(matchInfo)
        			self.matchMenu[currentCount] = matchItem
        			#print (matchItem)
        			#self.listofGtkItems[currentCount].set_label(matchInfo['score_summary'] + matchInfo['status'])
        			print ("updating : ", self.menu.get_children()[currentCount].get_label() , currentCount+1)
        			
        			self.menu.get_children()[currentCount].set_label(matchInfo['score_summary']+ "\n" +matchInfo['status'] + "   "+ str(currentCount)) 
        			itemToBeRemoved = self.menu.get_children()[currentCount]
        			self.remove_menu(itemToBeRemoved)
        			self.add_menu(matchItem['gtkSummary'],currentCount)
        			self.menu.get_children()[currentCount].set_label(matchInfo['score_summary']+ "\n" +matchInfo['status'] + "   "+ str(currentCount))
        		currentCount += 1
        	


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

    def set_indicator_label(self, label):
    	self.indicator.set_label(label, "Cricket Score Indicator")

    def add_menu(self, widget, pos):
        self.menu.insert(widget, pos)

    def remove_menu(self, widget):
        self.menu.remove(widget)

    def set_menu_label(self, widget, label):
        widget.set_label(label)


    def showClicked(self,widget,matchItem):
    	self.indicatorLabelId =  matchItem['id']
    	self.set_indicator_label(matchItem['gtkSummary'].get_label())

    def updateData(self):
    	start = time.time() # get UNIX time

    	while True:
            duration = time.time() - start # resolution of 1 second is guaranteed
            if duration < REFRESH_INTERVAL: # sleep if we still have some time left before website update
                continue
            else:
            	self.updateLabels()
            	start = time.time() # get UNIX time
           		

    def createMatchItem(self,matchInfo):
    	if matchInfo['score_summary']:
	    	matchItem = {
	    		"gtkSummary": Gtk.MenuItem.new_with_label(matchInfo['score_summary'] + matchInfo['status']),
	    		"gtkSubMenu": Gtk.Menu.new(),
	    		"gtkSetAsLabel": Gtk.MenuItem.new_with_label("Set As Label"),
	    		"id":		matchInfo['id'],
	    		"status": matchInfo['status'],
	    		"extra_info": matchInfo['extra_info'],
	    		"url": matchInfo['url'],
	    		"openInBrowser" : Gtk.MenuItem.new_with_label("Open in Browser"),
	    		"leauge": matchInfo["leauge"],

	    	}
	    	matchItem['gtkSetAsLabel'].connect("activate",self.showClicked,matchItem)
	    	matchItem['openInBrowser'].connect("activate",self.openInBrowser,matchItem)
	    	matchItem['gtkSubMenu'].append(matchItem['gtkSetAsLabel'])
	    	matchItem['gtkSubMenu'].append(matchItem['openInBrowser'])
	    	matchItem['gtkSummary'].set_submenu(matchItem['gtkSubMenu'])
	    	matchItem['openInBrowser'].show()
    		matchItem['gtkSummary'].show()
    		matchItem['gtkSetAsLabel'].show()
    	else:

	    	matchItem = {
	    		"gtkSummary": Gtk.MenuItem.new_with_label(matchInfo['leauge'].upper()),
	    		"gtkSubMenu": Gtk.Menu.new(),
	    		"gtkSetAsLabel": Gtk.MenuItem.new_with_label("Set As Label"),
	    		"score_summary": matchInfo['league'].upper(),
	    		"id":		matchInfo['id'],
	    		"status": matchInfo['status'],
	    		"extra_info": matchInfo['extra_info'],
	    		"url": matchInfo['url'],
	    		"leauge": matchInfo["leauge"],

	    	}
	    	matchItem['gtkSummary'].show()
	    	matchItem['gtkSummary'].set_sensitive(False)


    	
    	


    	return matchItem

    def openInBrowser(self,widget,matchItem):
    	webbrowser.open(matchItem['url'])



def run():
    myIndicator = scores_ind()
    myIndicator.main()

if __name__ == "__main__":
    print ("Use 'footballscore_indicator' to run the applet")
    myIndicator = scores_ind()
    myIndicator.main()
