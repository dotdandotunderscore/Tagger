import random
import numpy as np
import pandas as pd
import discord
from discord.ext import commands
from discord.utils import get
import shutil, pathlib, os, sys

class DayPlayCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.databasepath = os.path.join(pathlib.Path(__file__).parents[1], 'player_database.csv')
		self.playercodespath = os.path.join(pathlib.Path(__file__).parents[1], 'playercodes.txt')
		self.collectioncodespath = os.path.join(pathlib.Path(__file__).parents[1], 'collectioncodes.txt')
		self.dayplay_gridpath = os.path.join(pathlib.Path(__file__).parents[1], 'dayplay_grid.csv')
		self.dayplay_targetpath = os.path.join(pathlib.Path(__file__).parents[1], 'dayplay_target.csv')

	@commands.command(brief='', description='')
	@commands.has_role('Moderator')
	async def reset_dayplay(self, ctx):
		"""Takes grid ref in form [row][col] (i.e. 3A), and performs self.flipper on it."""
		await ctx.message.delete()
		backuppath = os.path.join(pathlib.Path(__file__).parents[1], 'backupdatabase', 'dayplay_grid.csv')
		newpath = os.path.join(pathlib.Path(__file__).parents[1], 'dayplay_grid.csv')
		shutil.copy(backuppath, newpath)
		zombie_dayplay = discord.utils.get(ctx.message.guild.text_channels, name='zombie-dayplay')
		zombie_dayplay_message = await zombie_dayplay.fetch_message(id=683961734897205264)
		zombie_target_message = await zombie_dayplay.fetch_message(id=683964775872331787)
		dayplay_grid = np.loadtxt(self.dayplay_gridpath, dtype=int, delimiter=',')
		dayplay_target = np.loadtxt(self.dayplay_targetpath, dtype=int, delimiter=',')
		zombie_dayplay_content = 'Current Grid: \n'
		for i in dayplay_grid:
			row_content = '| \t'
			for j in i:
				row_content += str(j)+'\t | \t'
			zombie_dayplay_content+=row_content+'\n'
		# zombie_dayplay_content+='\`\`\`'
		await zombie_dayplay_message.edit(content=zombie_dayplay_content)
		zombie_target_content = 'Target Grid: \n'
		for i in dayplay_target:
			row_content = '| \t'
			for j in i:
				row_content += str(j)+'\t | \t'
			zombie_target_content+=row_content+'\n'
		# zombie_target_content+='\`\`\`'
		await zombie_target_message.edit(content=zombie_target_content)
		zombie_complete_message = await zombie_dayplay.fetch_message(id=683970727573323807)
		await zombie_complete_message.edit(content='Dayplay incomplete.')
		return

	@commands.command(brief='Collect a playercode.', description='.collect [player code] [collection code]: Collects a player code.')
	@commands.has_role('Human')
	async def collect(self, ctx, playercode, collectioncode):
		playercodes = np.loadtxt(self.playercodespath, dtype=str, delimiter=',')
		player_codes_row = np.where(playercodes[:,0] == playercode)
		if len(player_row[0]) == 0:
			await ctx.send('Playercode not found.')
			return
		collectioncodes = np.loadtxt(self.collectioncodespath, dtype=str, delimiter=',')
		collection_row = np.where(collectioncodes[:,0] == collectioncode)
		if len(collection_row[0]) == 0:
			await ctx.send('Collection code not found.')
			return

		playercodes = np.delete(playercodes, player_codes_row[0][0])
		collectioncodes = np.delete(collectioncodes, collection_row[0][0])
		np.savetxt(self.playercodespath, playercodes)
		np.savetxt(self.collectioncodespath, collectioncodes)
		await ctx.send('Playercode collected: ' + playercode + ' with ' + collectioncode + '.')
		return

	@commands.command(brief='', description='')
	@commands.has_role('Moderator')
	async def end_human_dayplay(self, ctx):
		playercodes = np.loadtxt(self.playercodespath, dtype=str, delimiter=',')
		chosen_human = random.choice(playercodes)
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		player_row = np.where(player_database[:,7] == chosen_human)
		if len(player_row[0]) == 0:
			await ctx.send('Randomly chosen code not found. Please try again.')
			return
		player_index = player_row[0][0]
		await ctx.send('Chosen Human: ' + player_database[int(player_index)][1] + ' ' + player_database[int(player_index)][2] + '. Tag them with braincode: ' + player_database[int(player_index)][4] + '.')
		return

	def flipper(self, ctx, row, column, dayplay_grid):
		"""Grid Day One - swap all adjacent elements."""
		row_els_to_flip = [-1,1]
		col_els_to_flip = [-1,1]
		num_rows = len(dayplay_grid)
		num_cols = len(dayplay_grid[0])

		for i in row_els_to_flip:
			if i+row < num_rows and i+row >=0:
				if dayplay_grid[int(i+row)][int(column)] == 0:
					dayplay_grid[int(i+row)][int(column)] = 1
				else:
					dayplay_grid[int(i+row)][int(column)] = 0

		for j in col_els_to_flip:
			if j+column < num_cols and j+column >= 0:
				if dayplay_grid[int(row)][int(j+column)] == 0:
					dayplay_grid[int(row)][int(j+column)] = 1
				else:
					dayplay_grid[int(row)][int(j+column)] = 0

		return dayplay_grid

	@commands.command(brief='', description='')
	@commands.has_role('Zombie')
	async def activate(self, ctx, grid_ref):
		"""Takes grid ref in form [col][row] (i.e. A3), and performs self.flipper on it."""
		columns_dict = {'A':0, 'a':0, 'B':1, 'b':1, 'C':2, 'c':2, 'D':3, 'd':3, 'E':4, 'e':4, 'F':5, 'f':5, 'G':6, 'g':6, 'H':7, 'h':7, 'I':8, 'i':8}
		rows_dict = {'1':0, '2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7, '9':8}
		dayplay_grid = np.loadtxt(self.dayplay_gridpath, dtype=int, delimiter=',')
		if int(rows_dict[grid_ref[1]]) < len(dayplay_grid) and int(columns_dict[grid_ref[0]]) < len(dayplay_grid[0]):
			zombie_dayplay = discord.utils.get(ctx.message.guild.text_channels, name='zombie-dayplay')
			dayplay_grid = np.loadtxt(self.dayplay_gridpath, dtype=int, delimiter=',')
			row = int(rows_dict[grid_ref[1]])
			column = int(columns_dict[grid_ref[0]])
			dayplay_grid = self.flipper(ctx, row, column, dayplay_grid)
			pd.DataFrame(dayplay_grid).to_csv(self.dayplay_gridpath, header=None, index=None)
			zombie_dayplay_content = 'Current Grid: \n'
			for i in dayplay_grid:
				row_content = '| \t'
				for j in i:
					row_content += str(j)+'\t | \t'
				zombie_dayplay_content+=row_content+'\n'
			# zombie_dayplay_content+='\`\`\`'
			zombie_dayplay_message = await zombie_dayplay.fetch_message(id=683961734897205264)
			await zombie_dayplay_message.edit(content=zombie_dayplay_content)
			dayplay_target = np.loadtxt(self.dayplay_targetpath, dtype=int, delimiter=',')
			zombie_complete_message = await zombie_dayplay.fetch_message(id=683970727573323807)
			for i in range(0, len(dayplay_grid)):
				for j in range(0, len(dayplay_grid[0])):
					if dayplay_grid[i][j] != dayplay_target[i][j]:
						await zombie_complete_message.edit(content='Dayplay incomplete.')
						return
		await zombie_complete_message.edit(content='Dayplay complete!')


def setup(bot):
	bot.add_cog(DayPlayCommands(bot))
