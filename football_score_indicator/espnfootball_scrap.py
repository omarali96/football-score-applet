
from __future__ import print_function
import sys
import requests
from bs4 import BeautifulSoup
import collections

BASE_URL = "http://espnfc.us"
SUMMARY_URL = BASE_URL + "/scores/xhr?=1"

def get_matches_summary():
	try:
		summary = (requests.get("http://www.espnfc.us/scores?xhr=1", timeout = 5)).json()
	except Exception as err:
	    print ('get_matches_summary: Exception: ', err, file=sys.stderr)
	    return None

	soup = BeautifulSoup(summary['content']['html'], "lxml")
	soup = soup.findAll("div", id="score-leagues");
	#print "----------"
	#print soup
	#print "\n\n"*20
	#print soup[0]
	#print "----"
	#print "\n"
	#print x.get_text()#
	dictionaryOfLeagues = {}
	dictionaryOfMatches = {}
	for leagues in soup:
		#print "======================="
		leauge = leagues.findAll("div",{"class":"score-league"})
		#print len(leauge)
		#name = leauge.find("h4")
		#print name.get_text.strip()

		#extracting leauges

		for match in leauge:
			nameOfLeague = match.find("h4")
			dictionaryOfMatches = {}
			x = match.findAll("div",{"class":"score-group"})

			#extracting all matches in the current league

			for y in x:
				#print "----------------"*40
				#print y
				#print y.get_text()
				x = y.find("p")
				#print "\n"
				"""
				if(x is not None):
					#print x.get_text().strip()
					#print "---"*40
				"""
				#print "\n\n\n\n\n\n\n\n\n\n"

				datas = y.findAll("div",{"class":"score-box"})
				#print data
				if datas:
					for data in datas:
						team_names = data.findAll("div",{"class":"team-name"})
						"""
						print "-----"
						for team_name in team_names:
							print team_name.get_text().strip()
							print "\n"
						"""

						scores = data.findAll("div",{"class":"team-scores"})
						score = scores[0].findAll("span")

						score_summary = team_names[0].get_text().strip()
						if score[0].get_text().strip():
							score_summary += " : " +  score[0].get_text().strip()

						score_summary += " v "
						#print (score_summary)
						score_summary += team_names[1].get_text().strip()
						if score[1].get_text().strip():
							score_summary += " : " +  score[1].get_text().strip()

	 					#print (score_summary)
						idy = data.find("div",{"class":"score full"})
						#print idy['data-gameid']




						live = data.find("div",{"class":"game-info"})
						status = ""
						if live:
							#print "===="
							spans = live.findAll("span")
							for span in spans:
								status += span.get_text().strip() + " "

						#print status


						link = data.find("a",{"class":"primary-link"})
						#print link['href']

						extra_info = data.find('div',{"class":"extra-game-info"})
						info = ""
						if extra_info:

							spans = extra_info.findAll('span')
							for span in spans:
								info +=  span.get_text().strip() + " "

						match = {}
						match['id'] = idy['data-gameid']
						match['score_summary'] = score_summary
						match['url'] = link['href']
						match['status'] = status
						match['extra_info'] = info
						match['leauge'] = nameOfLeague.get_text().strip()

						dictionaryOfMatches[idy['data-gameid']] = match

			dictionaryOfLeagues[nameOfLeague.get_text().strip()] = dictionaryOfMatches

		"""
		for i in dictionaryOfLeagues:
			print (i)
			print (dictionaryOfLeagues[i])

		print( dictionaryOfLeagues)
		"""
	return dict(dictionaryOfLeagues)
