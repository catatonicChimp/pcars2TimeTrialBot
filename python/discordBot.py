# Work with Python 3.6
import discord
from discord.ext import commands
import urllib
import lxml
from bs4 import BeautifulSoup
import yaml
import os
import logging
# import pandas as pd
# import numpy
import texttable
import random

logging.basicConfig(level=logging.INFO)


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
		self.scrapeData()


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
					cleanRow = {"Rank": data[0], "Name": data[2].rstrip(), "Vehicle": data[3], "LapTime": self.cleanTime(data[6]), "Sector1": self.cleanTime(splitTimes[0].split(": ")[1].strip()), "Sector2": self.cleanTime(splitTimes[1].split(": ")[1].strip()), "Sector3": self.cleanTime(splitTimes[2].split(": ")[1].strip()),
								"GlobalGap": data[8], "LocalGap": ""}#, "Upload": data[15]}
					ranks.append(cleanRow)

		self.leaderBoardData = ranks


	def calculateGapTime(self, data):
		fastestTime = data[0]["LapTime"]
		for n in range(len(data)):
			if n == 0:
				data[0]["LocalGap"] = 0.000
				continue
			data[n]["LocalGap"] = data[n]["LapTime"] - fastestTime

		return data

	def cleanTime(self, lapTime):
		lapTimeValue = lapTime.split(":")
		minutes = int(lapTimeValue[0])
		seconds = float(lapTimeValue[1])
		result = (60 * minutes) + seconds
		return result


	def getLeaderTime(self):
		for rank in self.leaderBoardData:
			if rank["Rank"] == "1":
				leaderTime = rank
		return leaderTime

	def getOurTimes(self):
		self.scrapeData()
		ourTimes = []
		for rank in self.leaderBoardData:
			if rank["Name"] in self.names:
				ourTimes.append(rank)
		data = self.calculateGapTime(ourTimes)
		tableResult = self.makeTable(data)
		return tableResult

	def makeTable(self, data):
		table = texttable.Texttable()
		table.set_cols_align(["r", "l", "l", "c", "c", "c", "c", "c", "c"])
		table.header(data[0].keys())
		for row in data:
			table.add_row(row.values())
		table.set_max_width(0)
		return(f"```{table.draw()}```")

	def randomCar(self):
		result = random.choice(list(self.cars.keys()))
		return result

	def randomTrack(self):
		result = random.choice(list(self.tracks.keys()))
		return result


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
			self.dumpYml()
			return name
		else:
			return None

	def removeName(self, name):
		if name in self.names:
			self.names.remove(name)
			self.dumpYml()
			return name
		else:
			return None

	def setCar(self, car):
		if car in self.cars:
			self.car = car
			self.carid = self.cars[self.car]
			self.dumpYml()
			return 1
		else:
			return 0


	def setTrack(self, track):
		if track in self.tracks:
			self.track = track
			self.trackid = self.tracks[self.track]
			self.dumpYml()
			return 1
		else:
			return 0

bot = commands.Bot(command_prefix="?", description="Time Trail Bot")

@bot.command()
async def getTimes(ctx):
	"""
	Get all Times for Current Track/Car
	:param ctx:
	:return:
	"""
	await ctx.send(m.getOurTimes())

@bot.command()
@commands.has_permissions(administrator=True)
async def addUser(ctx, user):
	"""
	Add user to search list for track times.
	:param ctx:
	:param user:
	:return:
	"""
	name = m.addName(user)
	if name:
		await ctx.send(f"Added {name} to User List")
	else:
		await ctx.send(f"Couldn't add {user}, it already exists")



@bot.command()
@commands.has_permissions(administrator=True)
async def removeUser(ctx, user):
	"""
	Remove a User from the Search List
	:param ctx:
	:param user:
	:return:
	"""
	name = m.removeName(user)
	if name:
		await ctx.send(f"Remove {name} from User List")
	else:
		await ctx.send(f"Couldn't find {user} in User List")


@bot.command()
@commands.has_permissions(administrator=True)
async def setTrack(ctx, track):
	"""
	Set the Track
	:param ctx:
	:param track:
	:return:
	"""
	trackSet = m.setTrack(track)
	if trackSet == 1:
		await ctx.send(f"Track set to: {track}")
	else:
		await ctx.send(f"Invalid Track Name: {track}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setCar(ctx, car):
	"""
	Set the Car
	:param ctx:
	:param car:
	:return:
	"""
	carSet = m.setCar(car)
	if carSet == 1:
		await ctx.send(f"Car set to: {car}")
	else:
		await ctx.send(f"Invalid Car Name: {car}")


@bot.command()
async def randomCar(ctx):
	"""
	Get a Random Car
	:param ctx:
	:return:
	"""
	await ctx.send(f"Random Car: {m.randomCar()}")

@bot.command()
async def randomTrack(ctx):
	"""
	Get a Random Car
	:param ctx:
	:return:
	"""
	await ctx.send(f"Random Track: {m.randomTrack()}")

@bot.command()
async def randomCarTrack(ctx):
	"""
	Get Random Car and Track
	:param ctx:
	:return:
	"""
	await ctx.send(f"Random Car: {m.randomCar()}")
	await ctx.send(f"Random Track: {m.randomTrack()}")

# @bot.command()
# @commands.has_permissions(administrator=True)
# async def saveData(ctx):
# 	"""
# 	Saves the Data to Disk
# 	:param ctx:
# 	:return:
# 	"""
# 	m.dumpYml()

@bot.command()
async def timeTrialDetails(ctx):
	"""
	Retrieve Current Car/Track for Time Trial
	:param ctx:
	:return:
	"""
	await ctx.send(f"Car: {m.car}\nTrack: {m.track}")



@bot.event
async def on_ready():
	print(f"{bot.user.name} - {bot.user.id}")
	print(discord.__version__)
	print("Ready")


if __name__ == "__main__":
	token = os.getenv("TOKEN", None)
	if token:
		m = PCarsLeaderBoard()
		bot.run(token)
	else:
		print("No Token Found")
