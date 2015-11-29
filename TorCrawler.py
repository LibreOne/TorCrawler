#!/usr/bin/python
from bs4 import BeautifulSoup
import urllib.request, re, sys, sqlite3, time, os

rootFolder = os.path.dirname(os.path.realpath(__file__))
dbConn = sqlite3.connect(rootFolder+'/torcrawler.db')
c = dbConn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS Links (
	id integer primary key autoincrement, 
	title text, 
	oninoLink text unique, 
	hasBinCrawled integer, 
	lastCrawled date)""")
dbConn.commit()

class TorCrawler:
	def fetchLinksPage(self, url):
		print('\nFetch: '+str(url))
		page = urllib.request.urlopen(url)
		soup = BeautifulSoup(page, "html.parser")
		linkCounter=0
		for link in soup.findAll('a'):
			linkTitle = ""
			linkHref = link.get('href') 
			if linkHref.startswith('http'):
				linkPage = urllib.request.urlopen(linkHref)
				linkSoup = BeautifulSoup(linkPage, "html.parser")
				linkTitle = str(linkSoup.title.string)
				c.execute("INSERT OR IGNORE INTO Links values (null, ?,?,0,date('now'))", [linkTitle, linkHref])
				linkCounter +=1
				print('Append-link...')
				print('title: '+str(linkTitle))
				print('link: '+str(linkHref))
				dbConn.commit()
		print('\nLinks found: '+str(linkCounter)+' NEXT..\n')
	def __init__(self):
		global rootFolder
		if len(sys.argv) >1:
			if str(sys.argv[1])=="-help":
				print("-fetchsite\nFetch all links from a site into db.\n")
				print("-fetchfile\nFetch all links from a file into db.\n")
				print("-showdb\nShow all fetch link from db.\n")
				print("-savefile\nSave all Links in db, to an txt-file.\n")
				print("-DELETE-ALL-LINKS\nDelete all link in database's Links-table.\n")
			elif str(sys.argv[1])=="-fetchsite" and len(str(sys.argv[2])) >0:
				print("Parser site: "+str(sys.argv[2]))
				self.fetchLinksPage(sys.argv[2])
			elif str(sys.argv[1])=="-fetchfile" and len(str(sys.argv[2])) >0:
				pathToFile = str(rootFolder)+'/'+str(sys.argv[2])
				if os.path.exists(pathToFile):
					txtFile = open(pathToFile)
					print('\n--------------------------------------------------')
					for link in txtFile.readlines():
						self.fetchLinksPage(link)
					print('\n--------------------------------------------------')					
					print("All found links is save to database.")
					print("-fetchfile "+str(sys.argv[2])+" IS DONE!")
				else:
					print("ERROR: Can't find the filepath:"+str(pathToFile))
			elif str(sys.argv[1])=="-showdb":
				print("SQL: SELECT * FROM Links")
				c.execute("SELECT * FROM Links")
				linkCounter=0
				for row in c:
					print (row)
					linkCounter +=1
				print('\n--------------------------------------------------')
				print('Total number of links in database: '+str(linkCounter))
			elif str(sys.argv[1])=="-DELETE-ALL-LINKS":
				print("SQL: DELETE FROM Links")
				c.execute("DELETE FROM Links")
				dbConn.commit()
				print("Query is now DONE!")
			elif str(sys.argv[1])=="-savefile" and len(str(sys.argv[2])) >0:
				targetFile = open(rootFolder + str(sys.argv[2]), 'w')
				targetFile.truncate()
				c.execute('SELECT * FROM Links')
				for row in c:
					targetFile.write(str(row[2]))
					targetFile.write('\n')
				targetFile.close()
				print('Links from database is saved to...')
				print(rootFolder+str(sys.argv[2]))
			else:
				print("TorCrawler.py -help")
if __name__=="__main__":
	TorCrawler()
#Depentences
#install: C:\Python34\Scripts>pip.exe install BeautifulSoup4