import random
import numpy as np
import pandas as pd
import discord
from discord.ext import commands
from discord.utils import get
import shutil, pathlib, os, sys
import asyncio
import StarvingMod as starve

Tagger = commands.Bot(command_prefix=".", description='A bot for running HvZ games.', intents=discord.Intents.all())

initial_extensions = ['cogs.player_commands',
					  'cogs.moderator_commands',
					  'cogs.admin_commands']

if __name__ == '__main__':
	for extension in initial_extensions:
		Tagger.load_extension(extension)

async def starving_bg():
	""" Background function for handling player starving."""
	await Tagger.wait_until_ready()
	while not Tagger.is_closed():
		try:
			player_database = np.loadtxt(os.path.join(pathlib.Path.cwd(), 'player_database.csv'), dtype=str, delimiter=',')
			next_starve_time, next_starve_player = 20000000000, None
			# Loops through player database, starving any player whose starve time has pased
			for i in player_database:
				if str(i[0]) == "User ID":
					error = 1
				elif str(i[0]) == "test1":
					error = 1
				elif str(i[5]) == 'Corpse':
					error = 1
				elif str(i[5]) == 'Human':
					error = 1
				elif starve.checkIfStarved(i):
					i[5] = 'Corpse'
					# Insert Guild ID here
					guildIDstr = np.loadtxt('guildID.txt', dtype=str)
					guild = Tagger.get_guild(int(guildIDstr))
					starved = discord.utils.get(guild.members, id = int(i[0]))
					await starved.remove_roles(discord.utils.get(guild.roles, name='Zombie'))
					await starved.add_roles(discord.utils.get(guild.roles, name='Corpse'))
					await discord.utils.get(guild.text_channels, name='game-announcements').send('Player ' + starved.mention + ' has starved.')
				# If the player hasnt starved and is a Zombie, checks if they are the next player to starve
				elif str(i[5]) == 'Zombie':
					next_starve_time, next_starve_player = starve.findNextStarve(i, next_starve_time, next_starve_player)
			# Updates database
			pd.DataFrame(player_database).to_csv(os.path.join(pathlib.Path.cwd(), 'player_database.csv'), header=None, index=None)
			#calculate the difference between the next starve time and right now
			#set sleepTime to that difference
			if next_starve_time == 20000000000:
				next_starve_time = 10+starve.getCurrentUTC()
			sleepTime = next_starve_time-starve.getCurrentUTC()
			if sleepTime != 10:
				print(sleepTime)
			await asyncio.sleep(sleepTime)
		except Exception as e:
			print('except:')
			print(str(e))
			await asyncio.sleep(10)

# Start-up operations
@Tagger.event
async def on_ready():
	# Aesthetic changes to bot profile
	await Tagger.change_presence(status=discord.Status.idle, activity=discord.Game('with Humans still'))
	print('Logged in as {0.user}'.format(Tagger))
	print('\n')
	return

# Runs bot
token = np.loadtxt('token.txt', dtype=str)
Tagger.loop.create_task(starving_bg())
Tagger.run(str(token), bot=True, reconnect=True)
