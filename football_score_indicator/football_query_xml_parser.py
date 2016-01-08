from xml.dom import minidom
import requests

"""
summary = (requests.get("http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20xml%20where%20url%3D%22http%3A%2F%2Fwww.espnfc.com%2Fgamepackage10%2Fdata%2Fgamecast%3FgameId%3D427503%26langId%3D0%26snap%3D0%22", timeout = 5))
print summary.content
file = summary.content
xmldoc = minidom.parseString (file)
print "\n-------------------------------------------------"
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
	print play.attributes['goal'].value
	print play.attributes['clock'].value
	for data in play.childNodes: 
		print data.nodeName + " : ",
		for x in data.childNodes:
			if x.nodeValue is not None:
				print x.nodeValue
				
"""

def queryXMLParsedResults(query):
	summary = (requests.get(query, timeout = 5))
	#print summary.content
	file = summary.content
	xmldoc = minidom.parseString (file)
	#print "\n-------------------------------------------------"
	teams = xmldoc.getElementsByTagName("teams")
	#print len(teams)
	#print teams[0].childNodes

	for team in teams[0].childNodes:
		#print team.childNodes[0].nodeValue
		pass

	gameInfo = xmldoc.getElementsByTagName("gameInfo")
	list = []
	for events in gameInfo[0].childNodes:
		#print events.nodeName + " : ",
		"""
		for value in events.childNodes:
			print value.nodeValue
		"""
	#print "\n-"*7
	shots = xmldoc.getElementsByTagName("shots")
	for play in shots[0].childNodes:
		#print play.attributes['goal'].value
		#print play.attributes['clock'].value
		for data in play.childNodes: 
			#print data.nodeName + " : ",
			if data.nodeName == 'result':
				list.append(data.childNodes[0].nodeValue)
	print list
	return list