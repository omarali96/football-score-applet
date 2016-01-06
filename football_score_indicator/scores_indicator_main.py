#!/usr/bin/env python

from gi.repository import Gtk,GObject,GdkPixbuf
from gi.repository import AppIndicator3 as appindicator

import pdb
from os import path
import threading
import time
import signal
import sys
import webbrowser

from espnfootball_scrap import ESPNFootballScrap

#time ot between each fetch
REFRESH_INTERVAL = 10

class scores_ind:

  def __init__(self):

    self.indicator = appindicator.Indicator.new("football-score-indicator",
      "football.png",appindicator.IndicatorCategory.APPLICATION_STATUS)

    self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    self.indicator.set_icon("./football.png")

    self.scrapObject = ESPNFootballScrap()
    self.indicatorLabelId = None
    self.indicator.set_label("Loading","")
    self.menu = Gtk.Menu().new()
    self.indicatorLabelId = None
    self.indicator.set_menu(self.menu)

    self.matchMenu = []
    self.addQuitAbout()

    while Gtk.events_pending():
      Gtk.main_iteration()
    self.updateLabels()
    while Gtk.events_pending():
      Gtk.main_iteration()
    
    thread = threading.Thread(target = self.updateDataAfterInterval)
    thread.daemon = True
    thread.start()


  def main(self):
    signal.signal(signal.SIGINT,signal.SIG_DFL)
    Gtk.main()

  def quit(self,widget):
    Gtk.main_quit()

  def addQuitAbout(self):
    about_item = Gtk.MenuItem("About")
    about_item.connect("activate",self.about)
    about_item.show()

    self.menu.append(about_item)

    quit_item = Gtk.MenuItem("Quit")
    quit_item.connect("activate",self.quit)
    quit_item.show()
    self.menu.append(quit_item)

  def about(self,widget):
    dialog = Gtk.AboutDialog.new()
    dialog.set_transient_for(widget.get_parent().get_parent())
    dialog.set_program_name("Football Score Indicator")
    dialog.add_credit_section("Credits here")
    dialog.set_license_type(Gtk.License.GPL_3_0)
    dialog.run()
    dialog.destroy()


  def setIndicatorLabel(self,label):
    self.indicator.set_label(label,"Football Score Indicator")


  def insertMenuItem(self,widget,pos):
    self.menu.insert(widget,pos)

  def removeMenuItem(self,widget):
    self.menu.remove(widget)

  def setMenuLabel(self,widget,label):
    widget.set_label(label)

  def showClicked(self,widget,matchItem):
    self.indicatorLabelId = matchItem['id']
    print "show clicked id is  :   ---   ",
    print matchItem['id']
    GObject.idle_add(self.setIndicatorLabel,matchItem['gtkSummary'].get_label())
    #self.setIndicatorLabel(matchItem['gtkSummary'].get_label())


  def updateDataAfterInterval(self):
    start = time.time()

    while True:
      duration = time.time() - start
      if duration >= REFRESH_INTERVAL:
        
        #print ("in updateDataAfterInterval in if")
        
        self.updateLabels()
        start= time.time()
        

  def updateLabels(self):
    #print "--------***********--------"
    
    leauges = self.scrapObject.get_matches_summary()
    if type(leauges) is list:
        print "\nit is list retruning....\n"
        return
    


    print leauges
    print type(leauges)
    previousLength = len(self.menu)-2
    
    #print previousLength
    
    """
    for i in self.menu:
      print i.get_label()

    print 
    print "-"*40
    print
    """

    currentCount = 0
    try:
        for leauge in leauges.keys():
          #pdb.set_trace()
          """
          print("currentCount : ", currentCount)
          print ("previousLength :", previousLength)
          """

          if previousLength <= currentCount:
            
            """
            print("In leauge, previous count ins less than current count , hence we insert")
            """

            newGtkItem = Gtk.MenuItem(leauge )
            self.menu.insert(newGtkItem, currentCount)
            newGtkItem.show()
            newGtkItem.set_sensitive(False)
            """
            print(" insert operation :", leauge, (currentCount +1))
            """

            self.matchMenu.append(leauge)
            currentCount += 1

            print "leauge inserted"

          else:
            """
            print ("In leauge, previous count is morethan the current count , hence we update")
            """

            self.menu.get_children()[currentCount].set_label(leauge + " updated "+ str(currentCount +1))

            """
            print("update operation :", leauge, (currentCount))
            print "submenu :",
            print self.menu.get_children()[currentCount].get_submenu()
            """


            if self.menu.get_children()[currentCount].get_submenu():
              self.menu.get_children[currentCount].remove_submenu()
            
            """
            print currentCount
            """

            self.menu.get_children()[currentCount].set_sensitive(False)


            self.matchMenu[currentCount]=  leauges[leauge]
            currentCount += 1

            print "leauge updated"

          for matches in leauges[leauge]:
            matchInfo = leauges[leauge][matches]


            print self.indicatorLabelId
            if(self.indicatorLabelId is None):
              
              print "it is none "
              
              self.indicatorLabelId = matchInfo['id']
            if self.indicatorLabelId == matchInfo['id']:
                print "setting indicator icon"
                if ":" in matchInfo['status']:
                    #self.setIndicatorLabel(matchInfo['score_summary'] + " starts at " + matchInfo['status'])
                    
                    GObject.idle_add(self.setIndicatorLabel,matchInfo['score_summary'] + " starts at " + matchInfo['status'])
                
                else:
                    
                    #self.setIndicatorLabel(matchInfo['score_summary'] + "  " + matchInfo['status'])
                    
                    GObject.idle_add(self.setIndicatorLabel, matchInfo['score_summary'] + "  " + matchInfo['status'])

            """
            print ("In match update")
            print ("current count : ", currentCount)
            print ("previousLength : ", previousLength)
            """

            if(previousLength <= currentCount):
              
              #print ("we insert a ,match item ")
              
              matchItem = self.createMatchItem(matchInfo)
              self.matchMenu.append(matchItem)
              self.menu.insert(matchItem['gtkSummary'],currentCount)
              matchItem['gtkSummary'].show()

              print ("matchi item inserted")
            else:
              widget = self.menu.get_children()[currentCount]
              
              #matchItem = self.createMatchItem(matchInfo,widget)
              #print type(self.matchMenu[currentCount]) is dict
              
              if type(self.matchMenu[currentCount]) is dict:
                
                #print "\n it is a dictionaru"
                GObject.idle_add(self.updateMenu,self.matchMenu[currentCount],matchInfo)
              else:
                
                #print "it is not a dictionary"
                
                matchItem = self.createMatchItem(matchInfo,widget)
                self.matchMenu[currentCount] = matchItem

                print ("matchitem was not dicationary updated")
              
              #print ("we update a match item")
            
            currentCount+=1
    except e:
        
        print e




  def createMatchItem(self,matchInfo, widget = None):

    if widget:
      matchItem = {

        "gtkSummary": widget,
        "gtkSubMenu": Gtk.Menu.new(),
        "gtkSetAslabel": Gtk.MenuItem("Set as Label"),
        "id": matchInfo["id"],
        "status": matchInfo['status'],
        "extraInfo": matchInfo['extra_info'],
        "url": matchInfo['url'],
        "OpenInBrowser": Gtk.MenuItem.new_with_label("Open in Browser"),
        "leauge": matchInfo["leauge"],
        "gtkSeperator1": Gtk.SeparatorMenuItem().new(),
        "gtkSeperator2": Gtk.SeparatorMenuItem().new(),
        "gtkSeperator3": Gtk.SeparatorMenuItem().new(),
        

        

        "gtkGoalHeading": Gtk.MenuItem("Goals"),
        "gtkGoalData": Gtk.MenuItem("Loading..."),
        "gtkStatus": Gtk.MenuItem("Loading..."),
        "gtkSubMenuScoreLabel": Gtk.MenuItem("Loading"),

      }
      if ":" in matchInfo['status']:
        matchItem['gtkSummary'].set_label(matchInfo['score_summary'] + " Starts at " + matchInfo['status'])    
      else:
            matchItem['gtkSummary'].set_label(matchInfo['score_summary'] + "\n " + matchInfo['status'])    

    else:
      matchItem = {
        "gtkSummary": Gtk.MenuItem.new_with_label(matchInfo['score_summary'] + "\n\t\t\t" + matchInfo['status']),
        "gtkSubMenu": Gtk.Menu.new(),
        "gtkSetAslabel": Gtk.MenuItem("Set as Label"),
        "id": matchInfo["id"],
        "status": matchInfo['status'],
        "extraInfo": matchInfo['extra_info'],
        "url": matchInfo['url'],
        "OpenInBrowser": Gtk.MenuItem.new_with_label("Open in Browser"),
        "leauge": matchInfo["leauge"],
        "gtkSeperator1": Gtk.SeparatorMenuItem().new(),
        "gtkSeperator2": Gtk.SeparatorMenuItem().new(),
        "gtkSeperator3": Gtk.SeparatorMenuItem().new(),
        

        

        "gtkGoalHeading": Gtk.MenuItem("Goals"),
        "gtkGoalData": Gtk.MenuItem("Loading..."),
        "gtkStatus": Gtk.MenuItem("Loading..."),
        "gtkSubMenuScoreLabel": Gtk.MenuItem("Loading"),

      }
      if ":" in matchInfo['status']:
        matchItem['gtkSummary'].set_label(matchInfo['score_summary'] + " Starts at " + matchInfo['status'])    
      else:
        matchItem['gtkSummary'].set_label(matchInfo['score_summary'] + "\n " + matchInfo['status'])    
 
    matchItem['gtkSetAslabel'].connect("activate",self.showClicked,matchItem)
    matchItem['OpenInBrowser'].connect("activate",self.OpenInBrowser,matchItem)
    matchItem['gtkSubMenu'].append(matchItem['gtkSetAslabel'])
    matchItem['gtkSubMenu'].append(matchItem['gtkSeperator1'])
    matchItem['gtkSubMenu'].append(matchItem['gtkSubMenuScoreLabel'])
    matchItem['gtkSubMenu'].append(matchItem['gtkStatus'])
    matchItem['gtkSubMenu'].append(matchItem['gtkSeperator2'])
    matchItem['gtkSubMenu'].append(matchItem['gtkGoalHeading'])
    matchItem['gtkSubMenu'].append(matchItem['gtkGoalData'])
    matchItem['gtkSubMenu'].append(matchItem['gtkSeperator3'])

    matchItem['gtkSubMenu'].append(matchItem['OpenInBrowser'])
    matchItem['gtkSummary'].set_submenu(matchItem['gtkSubMenu'])
    matchItem['OpenInBrowser'].show()
    matchItem['gtkSummary'].show()
    matchItem['gtkSetAslabel'].show()
    matchItem['gtkSeperator1'].show()
    matchItem['gtkSeperator2'].show()
    matchItem['gtkSeperator3'].show()
    matchItem['gtkGoalHeading'].show()
    matchItem['gtkGoalData'].show()
    matchItem['gtkSubMenuScoreLabel'].show()
    matchItem['gtkStatus'].show()
    return matchItem


  def OpenInBrowser(self,widget,matchItem):
    webbrowser.open(matchItem['url'])

  def updateMenu(self,widget,matchInfo):
    if ":" in matchInfo['status']:
      widget['gtkSummary'].set_label(matchInfo['score_summary'] + " starts at " + matchInfo['status'])
    else:
        widget['gtkSummary'].set_label(matchInfo['score_summary'] + "  " + matchInfo['status'])

    widget['gtkSetAslabel'].set_label("Set as Label ")
    widget['id'] = matchInfo['id']
    widget['status'] = matchInfo['status']
    widget['extraInfo'] = matchInfo['extra_info']
    widget['url'] = matchInfo['url']
    widget['leauge'] = matchInfo['leauge']
    print ("matchitem is dictionary updated")
    

def run():
  myIndicator = scores_ind()
  myIndicator.main()

if __name__ == "__main__":
  print ("use 'footnallscore_indicator to run the applet")
  myIndicator = scores_ind()
  myIndicator.main()