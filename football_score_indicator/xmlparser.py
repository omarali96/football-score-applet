from xml.dom import minidom

xmldoc = minidom.parse("yqlscore.xml")

teams = xmldoc.getElementsByTagName("teams")
print len(teams)
print teams[0].childNodes

for team in teams[0].childNodes:
	print team.childNodes[0].nodeValue


gameInfo = xmldoc.getElementsByTagName("gameInfo")

for events in gameInfo[0].childNodes:
	print events.nodeName + " : ",
	for value in events.childNodes:
		print value.nodeValue
print "\n-"*7
shots = xmldoc.getElementsByTagName("shots")
for play in shots[0].childNodes:
	print
	for data in play.childNodes: 
		print data.nodeName + " : ",
		for x in data.childNodes:
			if x.nodeValue is not None:
				print x.nodeValue
				