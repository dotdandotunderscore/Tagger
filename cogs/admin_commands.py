import random
import numpy as np
import pandas as pd
import discord
from discord.ext import commands
from discord.utils import get
import shutil, pathlib, os, sys
from datetime import datetime as dt, timedelta as timeD

class AdminCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.databasepath = os.path.join(pathlib.Path(__file__).parents[1], 'player_database.csv')
		self.memberspath = os.path.join(pathlib.Path(__file__).parents[1], 'members.csv')

	@commands.command(brief='Adds a user as a Non-Member.', description='.add_non_member @user: Gives a user the NonMember role.')
	@commands.has_any_role('Bot Dev', 'Committee')
	async def add_non_member(self, ctx):
		non_member = discord.utils.get(ctx.message.guild.roles, name='Non-Member')
		for user in ctx.message.mentions:
			await user.add_roles(non_member)
			await ctx.send('Added user ' + user.mention + ' as a Non-Member.')
			return

	# Used to print values in player_database to console
	@commands.command(brief='Sends logs', description='.check [option=Row] [option=Column]: Sends the specified part of the database.')
	@commands.has_any_role('Bot Dev', 'Committee')
	async def check(self, ctx, row = None, column = None):
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		if row == None:
			if column == None:
				for i in player_database:
					await ctx.send(i)
				return
		elif column == None:
			rowCheck = int(row)
			await ctx.send(player_database[rowCheck])
			return
		else:
			rowCheck = int(row)
			columnCheck = int(column)
			await ctx.send(player_database[rowCheck][columnCheck])
			return
		return

	@commands.command(brief='Resets the starve wall', description='.reset_starvewall: Resets the starve wall')
	@commands.has_any_role('Bot Dev', 'Committee')
	async def set_starvewall(self, ctx):
		starvelistpath = os.path.join(pathlib.Path(__file__).parents[1], 'starvelist.csv')
		starve_wall = discord.utils.get(ctx.message.guild.text_channels, name='the-starve-wall')
		starvelist_database = np.loadtxt(starvelistpath, dtype=str, delimiter=',')
		sorted_starvelist = starvelist_database[np.argsort(starvelist_database[:,1])]
		starve_wall_messagestr = np.loadtxt('starvewallmessageID.txt', dtype=str)
		starve_wall_message = await starve_wall.fetch_message(id=int(starve_wall_messagestr))
		starve_wall_content = ''
		for i in sorted_starvelist:
			if i[0] != 'User ID':
				if i[0] != 'test1':
					user = ctx.guild.get_member(int(i[0]))
					timestamp = dt.utcfromtimestamp(int(i[1])).strftime('%d/%m-%H:%M')
					starve_wall_content += user.mention + ' starves at ' + timestamp + '. \n'
		if starve_wall_content == '':
			starve_wall_content = 'Nobody is starving. Yet.'
		await starve_wall_message.edit(content=starve_wall_content)

	# De-rolls everyone
	@commands.command(brief='Removes all Human, Zombie, and Corpse roles.', description='.deroll_all: Removes all Human, Zombie, and Corpse roles.')
	@commands.has_any_role('Bot Dev', 'Committee')
	async def deroll_all(self, ctx):
		await ctx.send('Removing all Human and Zombie roles. This will take some time.')
		human = discord.utils.get(ctx.message.guild.roles, name='Human')
		zombie = discord.utils.get(ctx.message.guild.roles, name='Zombie')
		corpse = discord.utils.get(ctx.message.guild.roles, name='Corpse')
		for i in ctx.message.guild.members:
			await i.remove_roles(human)
			await i.remove_roles(zombie)
			await i.remove_roles(corpse)
		await ctx.send('All roles removed.')
		return

	# Reset player_database and starvelist
	@commands.command(brief='Resets the player database.', description='.reset_database: Resets the player database.')
	@commands.has_any_role('Bot Dev', 'Committee')
	async def reset_database(self, ctx):
		backuppath = os.path.join(pathlib.Path(__file__).parents[1], 'backupdatabase', 'player_database.csv')
		newpath = os.path.join(pathlib.Path(__file__).parents[1], 'player_database.csv')
		backuppath2 = os.path.join(pathlib.Path(__file__).parents[1], 'backupdatabase', 'starvelist.csv')
		newpath2 = os.path.join(pathlib.Path(__file__).parents[1], 'starvelist.csv')
		shutil.copy(backuppath, newpath)
		shutil.copy(backuppath2, newpath2)
		await ctx.send('Player database and starvelist reset.')
		return

	# Reset player_database
	@commands.command(brief='Runs all reset commands.', description='.reset_all: Runs all reset commands.')
	@commands.has_any_role('Bot Dev', 'Committee')
	async def end_game(self, ctx):
		await ctx.send('Starting reset, this will take some time.')
		reset_database = self.bot.get_command("reset_database")
		await ctx.invoke(reset_database)
		set_starvewall = self.bot.get_command("set_starvewall")
		await ctx.invoke(set_starvewall)
		deroll_all = self.bot.get_command("deroll_all")
		await ctx.invoke(deroll_all)
		await ctx.send('All reset.')
		return

	# Logs Tagger out
	@commands.command(brief='Kills Tagger.', description='Kills Tagger')
	@commands.has_any_role('Bot Dev', 'Committee')
	async def k(self, ctx):
		await ctx.send('help, im ded')
		await ctx.bot.logout()


def setup(bot):
	bot.add_cog(AdminCommands(bot))
