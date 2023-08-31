
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

class PlayerCommands(commands.Cog):
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
		### If the code below the comments doesn't work, replace with the code in comments
		#for i in range(1000):
		#	braincode = str(random.choice(words))+str(random.choice(words))+str(random.choice(words))
		#	if braincode in player_database:
		#		pass
		#	else:
		#		return braincode
		braincode = str(random.choice(words))+str(random.choice(words))+str(random.choice(words))
		if braincode in player_database:
			braincode = make_braincode(self,words, player_database)
		return braincode

	# New users use the Join command to add themselves to the Tagger database
	@commands.command(brief='Allows user to join the game in #join.', description='.join [student_number] or .join [Firstname] [Lastname]: Adds user to the game. You can only join with your name if you have been given the Non-Member role.')
	async def join(self, ctx, student_number, lastname = None):
		await ctx.message.delete()
		join = discord.utils.get(ctx.message.guild.text_channels, name='join')
		if ctx.channel == join:
			# Opens required resources
			player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
			words = np.loadtxt(self.wordspath, dtype=str)
			# If a student number was given, checks if they are a member
			member_index = False
			if lastname == None:
				members = np.loadtxt(self.memberspath, dtype=str, delimiter=',', skiprows=4)
				player_index = self.find(player_database[:,3], student_number)
				if player_index:
					await ctx.send('Student number in use already.')
					return
				member_index = self.find(members[:,5], student_number)
				if not member_index:
					await ctx.send('Membership not found. Buy membership at: https://www.su.rhul.ac.uk/societies/a-z/hvz/'+'\n If you have been given the Non-Member role, you should .join with your First and Last name, separated by a space.')
					return
			# Checks if the user has already joined
			player_index = self.find(player_database[:,0], str(ctx.message.author.id))
			if player_index:
				await ctx.send('You have already joined the game.')
				return
			# Creates entry in player_database for the given student number, generates 3 word brain code,  sets role to Human
			braincode = self.make_braincode(words, player_database)
			if member_index:
				newplayer = np.array([ctx.message.author.id, members[int(member_index)][3][1:-1], members[int(member_index)][2][1:], student_number,
							braincode, 'Human', 0, 100])
			else:
				if discord.utils.get(ctx.message.author.roles, name='Non-Member'):
					newplayer = np.array([ctx.message.author.id, student_number, lastname, 'Non-Member',
								braincode, 'Human', 0, 100])
				else:
					await ctx.send('If attempting to join with your Firstname and Lastname, you must have been given the Non-Member role by an Admin.')
					return

			player_database = np.append(player_database, [newplayer], axis=0)
			pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
			await ctx.message.author.add_roles(discord.utils.get(ctx.message.guild.roles, name='Human'))
			if ctx.message.author != ctx.message.guild.owner:
				await ctx.message.author.edit(nick=str(player_database[-1][1] + ' ' + player_database[-1][2]))
			await ctx.send('Hi there ' + player_database[-1][1] + ' ' + player_database[-1][2] + '.')
			await ctx.message.author.send('Your braincode is: ' + braincode + '. Keep it secret, keep it safe.')
			return
		else:
			await ctx.send('The join command can only be used in ' + join.mention + '.')
			return

	# Check your braincode
	@commands.command(brief='PMs you your braincode.', description='.check_braincode: PMs you your braincode.')
	@commands.has_role('Human')
	async def check_braincode(self, ctx):
		await ctx.message.delete()
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		player_index = self.find(player_database[:,0], str(ctx.message.author.id))
		if player_index:
			await ctx.message.author.send('Your braincode is: ' + player_database[int(player_index)][4] + '. Keep it secret, keep it safe.')
			return
		await ctx.message.author.send('I can\'t find your braincode. Please contact a moderator.')
		return

	@commands.command(brief='Set a bounty on a Human.', description='.bounty \"Firstname Lastname\" "bounty reward"')
	@commands.has_role('Zombie')
	async def bounty(self, ctx, nickname, reward):
		bountywall = discord.utils.get(ctx.message.guild.text_channels, name='bounty-wall')
		bountied = discord.utils.get(ctx.message.guild.members, nick=nickname)
		await bountywall.send('A bounty has been set on ' + bountied.mention + ' by ' + ctx.message.author.mention + ' with a reward of: ' + reward + '.')

	@commands.command(brief='Check how many Zombies there are.')
	async def how_many_zombies(self, ctx):
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		val = 0
		for i in player_database:
			if i[5] == 'Zombie':
				val+=1
		await ctx.send('There are ' + str(val) + ' Zombies.')

	@commands.command(brief='Check how many Humans there are.')
	async def how_many_humans(self, ctx):
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		val = 0
		for i in player_database:
			if i[5] == 'Human':
				val+=1
		await ctx.send('There are ' + str(val) + ' Humans.')

	# Used by Zombies to tag Humans
	@commands.command(brief='Tag a Human with their braincode in #zombie-chat.', description='.tag [braincode] @[who you want to feed] @[who you want to feed] [option=Day/Month-Hour:Minute]: Tag a Human user. i.e. .tag firstsecondthird @friend1 @friend2 02\/06-17:30')
	async def tag(self, ctx, braincode, fed: commands.Greedy[discord.Member] = None, *, time_tagged: typing.Optional[str] = 'now'):
		zombiechat = discord.utils.get(ctx.message.guild.text_channels, name='zombie-chat')
		await ctx.message.delete()
		# Checks if .tag was run in zombie-chat
		if ctx.channel == zombiechat:
			# Opens database and sets initial parameters
			player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
			starvelist_database = np.loadtxt(self.starvelistpath, dtype=str, delimiter=',')
			death_messages = np.loadtxt(os.path.join(pathlib.Path(__file__).parents[1], 'death_messages.txt'), dtype=str, delimiter=',')
			humanchat = discord.utils.get(ctx.message.guild.text_channels, name='human-chat')
			starve_wall = discord.utils.get(ctx.message.guild.text_channels, name='the-starve-wall')
			# Checks player_database for tagged player
			player_index = self.find(player_database[:,4], braincode)
			if player_index:
				tagged = ctx.guild.get_member(int(player_database[int(player_index)][0]))
				# Ends command if player was a Zombie
				if discord.utils.get(tagged.roles, name = 'Zombie'):
					await ctx.send('Player is already a Zombie')
					return
				else:
					player_database[int(player_index)][5] = 'Zombie'
					# The below conditional statements handle starve timers
					# Calculates starve timer based on current time (if no time_tagged was passed) or
					# by converting time_tagged into utc and adding feed_ammount
					starve_time = 0
					if time_tagged == 'now':
						starve_time = int(time.mktime((dt.now() + self.feed_ammount).timetuple()))
					# Defaults to 'now' if tag is in future
					elif time.mktime((dt.strptime(str(dt.now().year)+'/'+time_tagged, '%Y/%d/%m-%H:%M')).timetuple()) > time.mktime(dt.now().timetuple()):
						await ctx.send('Tag time entered is in the future. Defaulting to now.')
						starve_time = int(time.mktime((dt.now() + self.feed_ammount).timetuple()))
					else:
						starve_time = int(time.mktime((dt.strptime(str(dt.now().year)+'/'+time_tagged, '%Y/%d/%m-%H:%M')+self.feed_ammount).timetuple()))
					# Sets starve time of tagged player
					player_database[int(player_index)][6] = starve_time
					# Finds "tagger" and sets their starve timer to time_tagged + feed_ammount if it is after their current starve timer
					# Does not set starve timer if tagger is not a Zombie
					if discord.utils.get(ctx.message.author.roles, name = 'Zombie'):
						tagger_index = self.find(player_database[:,0], str(ctx.message.author.id))
						if tagger_index:
							if starve_time > int(player_database[int(tagger_index)][6]):
								player_database[int(tagger_index)][6] = str(starve_time)
								tagger_starve_index = self.find(starvelist_database[:,0], str(ctx.message.author.id))
								if tagger_starve_index:
									starvelist_database[int(tagger_starve_index)][1] = str(starve_time)
								else:
									await ctx.send('Tagger not found in starve database.')
					# Finds mentioned players and sets their starve timer to time_tagged + feed_ammount if it is after their current starve timer
					if fed != None:
						check = 0
						for j in fed:
							check+=1
							fed_index = self.find(player_database[:,0], str(j.id))
							if fed_index:
								if player_database[int(fed_index)][5] == 'Zombie':
									if starve_time > int(player_database[int(fed_index)][6]):
										player_database[int(fed_index)][6] = str(starve_time)
										fed_starve_index = self.find(starvelist_database[:,0], str(j.id))
										if fed_starve_index:
											starvelist_database[int(fed_starve_index)][1] = str(starve_time)
										else:
											await ctx.send('Fed player not found in starve database.')
								else:
									await ctx.send('You can only feed Zombies.')
							else:
								await ctx.send('At least some of the mentioned players were not found in database.')
							if check == 2:
								break
					# If no players mentioned, automatically finds the players with the two lowest starve timers and feeds them
					else:
						auto_feed_string = ''
						starve_times = starvelist_database[:,1]
						if len(starve_times) <= 3:
							# If only one or less players with a starve time
							pass
						elif len(starve_times) == 4 and "tagger_starve_index" in locals():
							# If there are two players with a starve time, and one of them performed the tag
							the_other_player = tagger_starve_index - 1
							if starve_time > int(starvelist_database[the_other_player][1]):
								other_starve = self.find(player_database[:,0], starvelist_database[the_other_player][0])
								if other_starve:
									player_database[int(other_starve)][6] = str(starve_time)
									starvelist_database[int(the_other_player)][1] = str(starve_time)
									other_user = ctx.guild.get_member(int(player_database[int(other_starve)][0]))
									auto_feed_string+=', ' + other_user.mention
						else:
							# Finds the entries of the starve database with the lowest starve times
							if "tagger_starve_index" in locals():
								# If a player with a starve time performed the tag
								pruned_starve_times = np.delete(starve_times, tagger_starve_index, 0)
								lowest_starve_index, second_lowest_index = np.argpartition(pruned_starve_times, 2)[:2]
								if lowest_starve_index >= tagger_starve_index:
									lowest_starve_index += 1
								if second_lowest_index >= tagger_starve_index:
									second_lowest_index += 1
							else:
								lowest_starve_index, second_lowest_index = np.argpartition(starve_times, 2)[:2]

							lowest_starve = self.find(player_database[:,0], starvelist_database[lowest_starve_index][0])
							second_lowest = self.find(player_database[:,0], starvelist_database[second_lowest_index][0])

							# sets those players starve times if the new time is later than their current one
							if starve_time > int(starvelist_database[lowest_starve_index][1]) and lowest_starve:
								player_database[int(lowest_starve)][6] = str(starve_time)
								starvelist_database[lowest_starve_index][1] = str(starve_time)
								lowest_user = ctx.guild.get_member(int(player_database[int(lowest_starve)][0]))
								auto_feed_string+=', ' + lowest_user.mention
							if starve_time > int(starvelist_database[second_lowest_index][1]) and second_lowest:
								player_database[int(second_lowest)][6] = str(starve_time)
								starvelist_database[second_lowest_index][1] = str(starve_time)
								second_user = ctx.guild.get_member(int(player_database[int(second_lowest)][0]))
								auto_feed_string+=', ' + second_user.mention

					# Updates the rolls of the tagged player and saves all changed data to player_database
					await tagged.add_roles(discord.utils.get(ctx.message.guild.roles, name='Zombie'))
					await tagged.remove_roles(discord.utils.get(ctx.message.guild.roles, name='Human'))
					pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
					player_starves_at = player_database[int(player_index)][6]
					starvelist_entry = np.array([tagged.id,player_starves_at])
					starvelist_database = np.append(starvelist_database, [starvelist_entry], axis=0)
					sorted_starvelist = starvelist_database[np.argsort(starvelist_database[:,1])]
					pd.DataFrame(starvelist_database).to_csv(self.starvelistpath, header=None, index=None)
					starve_wall_message = await starve_wall.fetch_message(id=682881431973920909)
					starve_wall_content = ''
					for i in sorted_starvelist:
						if i[0] != 'User ID':
							if i[0] != 'test1':
								user = ctx.guild.get_member(int(i[0]))
								timestamp = dt.utcfromtimestamp(int(i[1])).strftime('%d/%m-%H:%M')
								starve_wall_content += user.mention + ' starves at ' + timestamp + '. \n'
					await starve_wall_message.edit(content=starve_wall_content)

					# Everything below handles sending notifications to channels about the tag
					# Creates the text to show which players have been fed
					feed_string = ctx.message.author.mention
					if fed != None:
						check = 0
						for j in fed:
							check += 1
							feed_string += ', ' + j.mention
							if check == 2:
								break
					else:
						feed_string+= auto_feed_string
					# Sends message to zombie-chat
					await ctx.send('Congrats ' + ctx.message.author.mention + '! You have tagged ' +
									tagged.mention + '. Their braincode was: ' + player_database[int(player_index)][4] + '. They will starve at: ' +
									dt.utcfromtimestamp(int(player_database[int(player_index)][6])).strftime('%d/%m-%H:%M') + '.' +
									'\n Zombies fed by tag: ' + feed_string + '.')
					# Selects a death message and sends message to human-chat
					death_phrase = str(random.choice(death_messages))
					await humanchat.send(player_database[int(player_index)][1] + ' ' + player_database[int(player_index)][2] + ' has been tagged. ' + death_phrase +
										 ' Their braincode was: ' + player_database[int(player_index)][4] + '.')
					return
			await ctx.send('Player does not exist.')
			return
		else:
			await ctx.send('The tag command can only be used in ' + zombiechat.mention + '.')
			return

def setup(bot):
	bot.add_cog(PlayerCommands(bot))
