import random
import numpy as np
import pandas as pd
import discord
from discord.ext import commands
from discord.utils import get
import shutil, pathlib, os, sys
from datetime import datetime as dt, timedelta as timeD
sys.path.append(os.path.join(pathlib.Path(__file__).parents[1], 'StarvingMod'))
import StarvingMod as starve
import time
import typing

class ModeratorCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.databasepath = os.path.join(pathlib.Path(__file__).parents[1], 'player_database.csv')
		self.wordspath = os.path.join(pathlib.Path(__file__).parents[1], 'words.txt')
		self.memberspath = os.path.join(pathlib.Path(__file__).parents[1], 'members.csv')
		self.starvelistpath = os.path.join(pathlib.Path(__file__).parents[1], 'starvelist.csv')
		self.feed_ammount = timeD(days = 2)

	def find(self, check_in, check_for):
		player_row = np.where(check_in == check_for)
		# Checks that a player was found
		if len(player_row[0]) != 0:
			return player_row[0][0]
		else:
			return False

	def make_braincode(self, words, player_database):
		""" Handles brain code generation to prevent duplicates. """
		for i in range(1000):
			braincode = str(random.choice(words))+str(random.choice(words))+str(random.choice(words))
			if braincode in player_database:
				pass
			else:
				return braincode

	# Retrieves user brain code
	@commands.command(brief='Retrieve the braincode of a user.', description='.get_braincode \"[Username]\": PMs you the braincode of a given user.')
	@commands.has_role('Moderator')
	async def get_braincode(self, ctx, username):
		await ctx.message.delete()
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		user = ctx.guild.get_member_named(username)
		if user == None:
			await ctx.send('User not found.')
			return
		else:
			player_index = self.find(player_database[:,0], str(user.id))
			if player_index:
				await ctx.message.author.send('Username ' + user.nickname + ' has braincode ' + player_database[int(player_index)][4] + '.')
				return
			await ctx.send('User is not in game.')
			return

	# Revives a Zombie
	@commands.command(brief='Revives a Zombie.', description='.revive \"[Username]\": Revives a Zombie.')
	@commands.has_role('Moderator')
	async def revive(self, ctx, username):
		await ctx.message.delete()
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		starvelist_database = np.loadtxt(self.starvelistpath, dtype=str, delimiter=',')
		words = np.loadtxt(self.wordspath, dtype=str)
		user = ctx.guild.get_member_named(username)
		if user == None:
			await ctx.send('User not found.')
			return
		else:
			if not discord.utils.get(user.roles, name='Zombie'):
				await ctx.send('User is not a Zombie.')
				return
			else:
				player_index = self.find(player_database[:,0], str(user.id))
				if player_index:
					newbraincode = self.make_braincode(words, player_database)
					player_database[int(player_index)][4] = newbraincode
					player_database[int(player_index)][5] = 'Human'
					player_database[int(player_index)][6] = 0
					pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
					starve_index = self.find(starvelist_database[:,0], str(user.id))
					if starve_index:
						starvelist_database = np.delete(starvelist_database, int(starve_index), 0)
						pd.DataFrame(starvelist_database).to_csv(self.starvelistpath, header=None, index=None)
					await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name='Zombie'))
					await user.add_roles(discord.utils.get(ctx.message.guild.roles, name='Human'))
					await user.send('Congrats! You have been revived. Your new braincode is: ' + newbraincode + '. Keep it secret. Keep it safe.')
					await discord.utils.get(ctx.message.guild.text_channels, name='human-chat').send('Hey, who let ' + i[1] + ' ' + i[2] + ' back in here?')
					set_starvewall = self.bot.get_command("set_starvewall")
					await ctx.invoke(set_starvewall)
					await ctx.send(user.nickname + ' has been revived!')
					return
			await ctx.send('Player does not exist.')
			return

	# Revives a Zombie
	@commands.command(brief='Revives all Zombies.', description='.revive_all: Revives all Zombies.')
	@commands.has_role('Moderator')
	async def revive_all(self, ctx):
		await ctx.message.delete()
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		words = np.loadtxt(self.wordspath, dtype=str)
		zombie = discord.utils.get(ctx.message.guild.roles, name='Zombie')
		for user in zombie.members:
			player_index = self.find(player_database[:,0], str(user.id))
			if player_index:
				newbraincode = self.make_braincode(words, player_database)
				player_database[int(player_index)][4] = newbraincode
				player_database[int(player_index)][5] = 'Human'
				player_database[int(player_index)][6] = 0
				await user.remove_roles(zombie)
				await user.add_roles(discord.utils.get(ctx.message.guild.roles, name='Human'))
				await user.send('Congrats! You have been revived. Your new braincode is: ' + newbraincode + '. Keep it secret. Keep it safe.')
		pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
		backuppath = os.path.join(pathlib.Path(__file__).parents[1], 'backupdatabase', 'starvelist.csv')
		newpath = os.path.join(pathlib.Path(__file__).parents[1], 'starvelist.csv')
		shutil.copy(backuppath, newpath)
		set_starvewall = self.bot.get_command("set_starvewall")
		await ctx.invoke(set_starvewall)
		await ctx.send('All players revived!')
		return

	# Feeds a zombie
	@commands.command(brief='Feeds all mentioned zombies fully or for a specified amount of hours.', description='.feed @user @user ... [number of hours, default = game feed time]: Feeds all mentioned players for the specified amount of hours.')
	@commands.has_role('Moderator')
	async def feed(self, ctx, fed: commands.Greedy[discord.Member] = None, *, feed_for: typing.Optional[str] = 'default'):
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		starvelist_database = np.loadtxt(self.starvelistpath, dtype=str, delimiter=',')
		if fed != None:
			for j in fed:
				fed_index = self.find(player_database[:,0], str(j.id))
				if fed_index:
					if player_database[int(fed_index)][5] == 'Zombie':
						if feed_ammount == 'default':
							starve_time = int(time.mktime((dt.now() + self.feed_ammount).timetuple()))
						else:
							feed_hours = int(feed_for)
							custom_feed_ammount = timeD(hours = feed_hours)
							starve_time = int(time.mktime((dt.now() + custom_feed_ammount).timetuple()))
						player_database[int(fed_index)][6] = str(starve_time)
						fed_starve_index = self.find(starvelist_database[:,0], str(j.id))
						if fed_starve_index:
							starvelist_database[int(fed_starve_index)][1] = str(starve_time)
							await ctx.send('Fed ' + j.mention + '.')
						else:
							await ctx.send('Fed player not found in starve database.')
					else:
						await ctx.send('You can only feed Zombies.')
				else:
					await ctx.send('At least some of the mentioned players were not found in database.')
		await ctx.send('Done.')

	# Feeds a zombie
	@commands.command(brief='Feeds all zombies fully or for a specified amount of hours.', description='.feed_all [number of hours, default = game feed time]: Feeds zombies for the specified amount of hours.')
	@commands.has_role('Moderator')
	async def feed_all(self, ctx, feed_for = 'default'):
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		starvelist_database = np.loadtxt(self.starvelistpath, dtype=str, delimiter=',')
		for j in discord.utils.get(ctx.message.guild.members, role = 'Zombie'):
			fed_index = self.find(player_database[:,0], str(j.id))
			if fed_index:
				if feed_ammount == 'default':
					starve_time = int(time.mktime((dt.now() + self.feed_ammount).timetuple()))
				else:
					feed_hours = int(feed_for)
					custom_feed_ammount = timeD(hours = feed_hours)
					starve_time = int(time.mktime((dt.now() + custom_feed_ammount).timetuple()))
				player_database[int(fed_index)][6] = str(starve_time)
				fed_starve_index = self.find(starvelist_database[:,0], str(j.id))
				if fed_starve_index:
					starvelist_database[int(fed_starve_index)][1] = str(starve_time)
					await ctx.send('Fed ' + j.mention + '.')
				else:
					await ctx.send('Fed player not found in starve database.')
			else:
				await ctx.send('At least some of the mentioned players were not found in database.')
		await ctx.send('Done.')

	# Delete a players entry using their discord name and identifier
	@commands.command(brief='Deletes a player from the game.', description='.delete_player \"[Username]\": Deletes a player and their entry from the game.')
	@commands.has_role('Moderator')
	async def delete_player(self, ctx, username):
		####### Need to add removing from starvelist
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		user = ctx.guild.get_member_named(username)
		if user == None:
			await ctx.send('User not found.')
			return
		else:
			player_index = self.find(player_database, str(user.id))
			if player_index:
				player_database = np.delete(player_database, int(player_index), 0)
				pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
				await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name='Human'))
				await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name='Zombie'))
				await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name='Corpse'))
				await ctx.send('Player removed.')
				return

def setup(bot):
	bot.add_cog(ModeratorCommands(bot))
