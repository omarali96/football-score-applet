from gi.repository import Gtk,GObject,GdkPixbuf
from gi.repository import AppIndicator3 as appindicator

indicator = appindicator.Indicator.new("football-score-indicator",
  "",appindicator.IndicatorCategory.APPLICATION_STATUS)
# path.abspath(path.dirname(__file__))+"/football.png"
indicator.set_status(appindicator.IndicatorStatus.ACTIVE)


menu = Gtk.Menu()

menuitem = Gtk.MenuItem("this is menu item")

indicator.set_menu(menu)
menu.append(menuitem)
menuitem.show()

submenu = Gtk.Menu()
menuitem.set_submenu(submenu)


submenuitem = Gtk.MenuItem("This is submenu MenuItem")
submenu.append(submenuitem)
submenuitem.show()




GtkContainer.remove(menuitem,submenu)




Gtk.main()