#!/usr/bin/env python

from gi.repository import Gtk,GObject,GdkPixbuf
from gi.repository import AppIndicator3 as appindicator

from os import path
import threading
import time
import signal
import webbrowser

from espnfootball_scrap import ESPNFootballScrap
from football_query_xml_parser import queryXMLParsedResults
from Preferences import PreferencesWindow

#time ot between each fetch
REFRESH_INTERVAL = 10

class scores_ind:

  def __init__(self):

    self.indicator = appindicator.Indicator.new("football-score-indicator",
      path.abspath(path.dirname(__file__))+"/football.png",appindicator.IndicatorCategory.APPLICATION_STATUS)
    # path.abspath(path.dirname(__file__))+"/football.png"
    self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    self.indicator.set_icon(path.abspath(path.dirname(__file__))+"/football.png")

    self.scrapObject = ESPNFootballScrap()
    self.indicatorLabelId = None
    self.indicator.set_label("No Live Matches","")
    self.menu = Gtk.Menu().new()
    self.indicatorLabelId = None
    self.indicator.set_menu(self.menu)

    self.matchMenu = []
    self.addQuitAboutPreferences()

    while Gtk.events_pending():
      Gtk.main_iteration()
    self.updateLabels()
    while Gtk.events_pending():
      Gtk.main_iteration()




  def main(self):
    signal.signal(signal.SIGINT,signal.SIG_DFL)
    thread = threading.Thread(target = self.updateDataAfterInterval)
    print thread.name
    thread.daemon = True
    thread.start()
    Gtk.main()

  def quit(self,widget):
    print "--------------------------------->    quit clicked"
    # sys.exit(1)
    Gtk.main_quit()

  def addQuitAboutPreferences(self):
    preferences_item = Gtk.MenuItem('Preferences')
    preferences_item.connect("activate",self.preferences)
    preferences_item.show()
    self.menu.append(preferences_item)

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
    dialog.add_credit_section("Nishant Kukreja","")
    dialog.add_credit_section("Abhishek Rose","")
    dialog.set_license_type(Gtk.License.GPL_3_0)
    dialog.run()
    dialog.destroy()

  def preferences(self,widget):
    window = PreferencesWindow()
    window.display()



  def setIndicatorLabel(self,label):
    self.indicator.set_label(label,"Football Score Indicator")


  def insertMenuItem(self,widget,pos):
    self.menu.insert(widget,pos)

  def removeMenuItem(self,widget):
    self.menu.remove(widget)

  def setMenuLabel(self,widget,label):
    print "label is " + label
    widget.set_label(label)
    

  def showClicked_cb(self,widget,matchItem):
    if matchItem is None:
        print "showClicked_cb: early exit"
        return
    self.indicatorLabelId = matchItem['id']
    print "show clicked id is  :   ---   ",
    print matchItem['id']

    # NOTE: `idle_add` is not required here as we are in callback and
    # therefore can modify Gtk data structures
    # NOTE: this function seems to be causing crash
    # take a good look at the args passed to it
    self.setIndicatorLabel(matchItem['gtkSummary'].get_label())




  def updateDataAfterInterval(self):
    while True:
        start = time.time()
        self.updateLabels()
        # while Gtk.events_pending():
        #   Gtk.main_iteration()


        #self.setSubMenuData()
        duration = time.time() - start
        if duration < REFRESH_INTERVAL:
            time.sleep(REFRESH_INTERVAL-duration)

  def updateLabels(self):


    leauges=self.scrapObject.get_matches_summary()
    if type(leauges) is list:
      return


    previousLength = len(self.menu) - 3

    currentCount = 0

    for leauge in leauges.keys():

      newLeaugeItem = Gtk.MenuItem(leauge)
      newLeaugeItem.set_sensitive(False)
      if currentCount >= previousLength:
        GObject.idle_add(self.insertMenuItem,newLeaugeItem,currentCount)

        newLeaugeItem.show()

        self.matchMenu.append(leauge)


      else:

        if self.menu.get_children()[currentCount].get_submenu():
          #print "removing ------------------------------",
          #print self.menu.get_children()[currentCount].get_label()

          GObject.idle_add(self.removeMenuItem,self.menu.get_children()[currentCount])
          GObject.idle_add(self.insertMenuItem,newLeaugeItem,currentCount)
          newLeaugeItem.show()

        else:


          #print "updating -------------------------------",

          #print self.menu.get_children()[currentCount].get_label()

          GObject.idle_add(self.setMenuLabel,self.menu.get_children()[currentCount],leauge)
        self.matchMenu[currentCount] = leauge

      currentCount += 1






      for matches in leauges[leauge]:
        matchInfo = leauges[leauge][matches]

        if self.indicatorLabelId is None:
          self.indicatorLabelId = matchInfo['id']

        if self.indicatorLabelId == matchInfo['id']:
          if ":" in matchInfo['status']:
            GObject.idle_add(self.setIndicatorLabel,matchInfo['score_summary'] + " starts at " + matchInfo['status'])
          else:
            GObject.idle_add(self.setIndicatorLabel, matchInfo['score_summary'] + "  " + matchInfo['status'])


        if previousLength <= currentCount:

          matchItem = self.createMatchItem(matchInfo)
          self.matchMenu.append(matchItem)
          #print "insertin match ---------------- ",
          #print matchItem['gtkSummary']
          GObject.idle_add(self.insertMenuItem,matchItem['gtkSummary'],currentCount)
          matchItem['gtkSummary'].show()

        else:

          widget = self.menu.get_children()[currentCount]

          if type(self.matchMenu[currentCount]) is dict:
            self.updateMenu(self.matchMenu[currentCount],matchInfo)
            #print "updating match over match--------------------------------"
            #print self.matchMenu[currentCount]['gtkSummary'].get_label()


          else:
            matchItem = Gobject.idle_add(self.createMatchItem,matchInfo,widget)
            #print "updating match over leauge-----------------------",
            #print matchItem['gtkSummary'].get_label()
            self.matchMenu[currentCount] = matchItem

        currentCount += 1

  def createMatchItem(self,matchInfo, widget = None):

    if widget:
      matchItem = {

        "gtkSummary":       widget,
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
      if ":" in matchInfo['status']:
        #matchItem['gtkSummary'].set_label(matchInfo['score_summary'] + " Starts at " + matchInfo['status'])
        GObject.idle_add(self.setMenuLabel,matchItem['gtkSummary'],matchInfo['score_summary'] + " Starts at " + matchInfo['status'])
      else:
        #matchItem['gtkSummary'].set_label(matchInfo['score_summary'] + "\n " + matchInfo['status'])
        GObject.idle_add(self.setMenuLabel,matchItem['gtkSummary'],matchInfo['score_summary'] + "\n " + matchInfo['status'])
    else:
      matchItem = {
        "gtkSummary":                Gtk.ImageMenuItem.new_with_label(matchInfo['score_summary'] + "\t\t\t" + matchInfo['status']),
        "gtkSubMenu":                Gtk.Menu.new(),
        "gtkSetAslabel":             Gtk.MenuItem("Set as Label"),
        "id":                        matchInfo["id"],
        "status":                    matchInfo['status'],
        "extraInfo":                 matchInfo['extra_info'],
        "url":                       matchInfo['url'],
        "gtkOpenInBrowser":          Gtk.MenuItem.new_with_label("Open in Browser"),
        "leauge":                    matchInfo["leauge"],
        "gtkSeperator1":             Gtk.SeparatorMenuItem().new(),
        "gtkSeperator2":             Gtk.SeparatorMenuItem().new(),
        "gtkSeperator3":             Gtk.SeparatorMenuItem().new(),

        "gtkGoalHeading":       Gtk.MenuItem("Goals"),
        "gtkGoalData":          Gtk.MenuItem("Loading..."),
        "gtkStatus":            Gtk.MenuItem("Loading..."),
        "gtkSubMenuScoreLabel": Gtk.MenuItem("Loading"),

      }
      if ":" in matchInfo['status']:
        #matchItem['gtkSummary'].set_label(matchInfo['score_summary'] + " Starts at " + matchInfo['status'])
        GObject.idle_add(self.setMenuLabel,matchItem['gtkSummary'],matchInfo['score_summary'] + " Starts at " + matchInfo['status'])
      else:
        #matchItem['gtkSummary'].set_label(matchInfo['score_summary'] + "\n " + matchInfo['status'])
        GObject.idle_add(self.setMenuLabel,matchItem['gtkSummary'],matchInfo['score_summary'] + "\n " + matchInfo['status'])

    matchItem['gtkSetAslabel'].connect("activate",self.showClicked_cb,matchItem)
    matchItem['gtkOpenInBrowser'].connect("activate",self.OpenInBrowser_cb,matchItem)
    matchItem['gtkSubMenu'].append(matchItem['gtkSetAslabel'])
    matchItem['gtkSubMenu'].append(matchItem['gtkSeperator1'])
    matchItem['gtkSubMenu'].append(matchItem['gtkSubMenuScoreLabel'])
    matchItem['gtkSubMenu'].append(matchItem['gtkStatus'])
    matchItem['gtkSubMenu'].append(matchItem['gtkSeperator2'])
    matchItem['gtkSubMenu'].append(matchItem['gtkGoalHeading'])
    matchItem['gtkSubMenu'].append(matchItem['gtkGoalData'])
    matchItem['gtkSubMenu'].append(matchItem['gtkSeperator3'])

    matchItem['gtkSubMenu'].append(matchItem['gtkOpenInBrowser'])
    matchItem['gtkSummary'].set_submenu(matchItem['gtkSubMenu'])
    matchItem['gtkOpenInBrowser'].show()
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


  def OpenInBrowser_cb(self,widget,matchItem):
    webbrowser.open(matchItem['url'])


  def updateMenu(self,widget,matchInfo):
    
    #print widget.keys()
    if ":" in matchInfo['status']:
      #widget['gtkSummary'].set_label(matchInfo['score_summary'] + " starts at " + matchInfo['status'])
      GObject.idle_add(widget['gtkSummary'].set_label,matchInfo['score_summary'] + " starts at " + matchInfo['status'])
    else:
      #widget['gtkSummary'].set_label(matchInfo['score_summary'] + "  " + matchInfo['status'])
      GObject.idle_add(widget['gtkSummary'].set_label,matchInfo['score_summary'] + " " + matchInfo['status'])
      print widget['gtkSummary'].get_label()
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
    GObject.idle_add(self.setMenuLabel,widget['gtkSubMenuScoreLabel'],matchInfo['score_summary'] )

    #widget['gtkStatus'].set_label(matchInfo['status'])
    GObject.idle_add(self.setMenuLabel,widget['gtkStatus'],matchInfo['status'])
    widget['gtkStatus'].set_sensitive(False)

    #widget['gtkSetAslabel'].set_label("Set as Label ")

    GObject.idle_add(self.setMenuLabel,widget['gtkSetAslabel'],"Set as Label")



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





  def getQuery(self,id):
    query =     "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20xml%20where%20url%3D%22http%3A%2F%2Fwww.espnfc.com%2Fgamepackage10%2Fdata%2Fgamecast%3FgameId%3D"
    query +=     id
    query +=    "%26langId%3D0%26snap%3D0%22"
    return query






  def updateSubMenuLabels(self,id,widget):
    self.getQuery(id)

    goals = queryXMLParsedResults(self.getQuery(id))
    if not goals:
      #print "goals are not available"
      widget.set_label("No Goals Yet")
      return
    else:
      print "goals available"
      str = ""
      for i in goals:
        str += i.replace("<b>","").replace("</b>","").replace("<br>","") + "\n"
        #print str
      widget.set_label(str)





  def setSubMenuData(self):

    for i in self.matchMenu:
      if type(i) is dict:
        if( 'LIVE' in i['gtkStatus'].get_label() ):
          print "this is live"
          thread = threading.Thread(target=self.updateSubMenuLabels,args= ( i['id'], i['gtkGoalData']) )





def run():
  myIndicator = scores_ind()
  myIndicator.main()

if __name__ == "__main__":
  print ("use 'footnallscore_indicator to run the applet")
  myIndicator = scores_ind()
  myIndicator.main()
