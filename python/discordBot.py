# Work with Python 3.6
import discord
import urllib
import lxml
from bs4 import BeautifulSoup
# import time
from datetime import time, timedelta
import yaml
import os




class PCarsLeaderBoard(object):


	def __init__(self):
		self.PCARS2LEADERBOARD = "http://cars2-stats-steam.wmdportal.com/index.php"
		self.data = self.loadYml()
		self.cars = self.data['cars']
		self.tracks = self.data['tracks']
		self.names = self.data['names']
		self.car = self.data['car']
		self.track = self.data['track']
		self.carid = self.cars[self.car]
		self.trackid = self.tracks[self.track]
		self.leaderBoardData = self.scrapeData()


	def loadYml(self):
		with open('./python/config.yml', 'r') as f:
			data = yaml.load(f, Loader=yaml.FullLoader)
		return data

	def dumpYml(self):
		self.data['cars'] = self.cars
		self.data['tracks'] = self.tracks
		self.data['names'] = self.names
		self.data['car'] = self.car
		self.data['track'] = self.track
		with open('./python/config.yml', 'w') as f:
			yaml.dump(self.data, f, default_flow_style=False)

	def scrapeData(self):
		urlBase = '{0}/leaderboard?track={1}&vehicle={2}'.format(self.PCARS2LEADERBOARD, self.trackid, self.carid)
		document = urllib.request.urlopen(urlBase)
		soup = BeautifulSoup(document, "lxml")
		pages = soup.find(lambda tag: tag.name == 'select' and tag.has_attr('id') and tag['id'] == "pager_top_select_page")
		if pages:
			pages = pages.text.split()
		else:
			pages = [1]
		ranks = []
		for page in pages:
			url = "{0}&page={1}".format(urlBase, page)
			print(url)
			document = urllib.request.urlopen(url)
			soup = BeautifulSoup(document, "lxml")
			table = soup.find(lambda tag: tag.name == 'table' and tag.has_attr('id') and tag['id'] == "leaderboard")
			rows = table.findAll(lambda tag: tag.name == 'tr')

			for row in rows:
				data = row.text.strip()
				data = data.split("\n")
				if len(data) > 15:
					splitTimes = row.contents[7].attrs['title'].split("\n")
					cleanRow = {"rank": data[0], "user": data[2].rstrip(), "vehicle": data[3], "time": self.cleanTime(data[6]), "sector1": self.cleanTime(splitTimes[0].split(": ")[1].strip()), "sector2": self.cleanTime(splitTimes[1].split(": ")[1].strip()), "sector3": self.cleanTime(splitTimes[2].split(": ")[1].strip()),
								"gap": data[8], "uploaded": data[15]}
					ranks.append(cleanRow)
		return ranks

	def cleanTime(self, lapTime):
		lapTimeValue = lapTime.split(":")
		minutes = int(lapTimeValue[0])
		seconds = float(lapTimeValue[1])
		result = (60 * minutes) + seconds
		return result


	def getLeaderTime(self):
		for rank in self.leaderBoardData:
			if rank["rank"] == "1":
				leaderTime = rank
		return leaderTime

	def getOurTimes(self):
		ourTimes = []
		for rank in self.leaderBoardData:
			if rank["user"] in self.names:
				ourTimes.append(rank)
		return ourTimes

	def getUserTimes(self, name):
		for rank in self.leaderBoardData:
			if name == rank["user"]:
				return rank
			else:
				continue
		else:
			return None

	def addName(self, name):
		if name not in self.names:
			self.names.append(name)

	def removeName(self, name):
		self.names.remove(name)

	def setCar(self, car):
		self.car = car

	def setTrack(self, track):
		self.track = track








class Pcars2Bot(discord.Client):
	async def on_ready(self):
		print("Logged on as", self.user)

	async def on_message(self, message):
		if message.author == self.user:
			return

		if message.content == '!TimeTrial':
			await message.channel.send("This is a test of new code formatting and docker setup")

		if '!TimeTrialAddUser' in message.content:
			userAdd = message.content.split(" ")[-1]
			await message.channel.send("Adding User: {0}".format(userAdd))


# 	async def sendTrackTimes(self, message, carSet, trackSet):
# 			for key, value in trackDict.items():
# 				if key == trackSet:
# 					track = key
# 					trackid = value
# 			for key, value in carDict.items():
# 				if key == carSet:
# 					car = key
# 					carid = value
# 			times = updateTimes(carid, trackid)
# 			await message.channel.send("Current Time Trial Results for {0} at {1}:\n".format(car, track))
# 			for time in times["data"]:
# 				localGap = 0
# 				msg = """
# \n
# Username: @{0}
# Overal Rank: {1}
# Lap Time: {2}
# Gap to First Place: {3}
# Gap to Next Place ("Local"): {4}
# ===============================================
# 				""".format(time["user"], time["rank"], time["time"], time["gap"], localGap)
# 				await message.channel.send(msg)




if __name__ == "__main__":
	token = os.getenv("TOKEN", None)
	if token:
		m = PCarsLeaderBoard()
		client = Pcars2Bot()
		client.run(token)
	else:
		print("No Token Found")
