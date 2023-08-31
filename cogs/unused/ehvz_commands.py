import random
import numpy as np
import pandas as pd
from math import ceil
import asyncio
import discord
from discord.ext import commands
from discord.utils import get
import shutil, pathlib, os, sys
from datetime import datetime as dt, timedelta as timeD
sys.path.append(os.path.join(pathlib.Path(__file__).parents[1], 'StarvingMod'))
import StarvingMod as starve
import time
import typing

class EHvZCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.databasepath = os.path.join(pathlib.Path(__file__).parents[1],
							'player_database.csv')
		self.stun_timer = 'time here'
		self.class_list = ['collateral', 'reroll', 'heavy', 'ranged', 'explode', 'splash', 'fast', 'deflect']
		self.class_fights = [4,3,5,4,4,4,3,4]
		self.class_damages = [1,1,2,1,1,1,2,1]
		self.class_healths = [6,5,3,5,3,4,4,4]

	def find(self, check_in, check_for):
		player_row = np.where(check_in == check_for)
		# Checks that a player was found
		if len(player_row[0]) != 0:
			return player_row[0][0]
		else:
			return False


	def fight(self, ctx, attacker, defender, message_content, result, is_first_attack = None):
		# Anything to do with first_attack is deflect implementation
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		first_attack_hit = 0
		attacker_member, attacker_index, attacker_health = attacker
		defender_member, defender_index, defender_health = defender
		if result == 'Critical Success':
			if is_first_attack != None:
				human = discord.utils.get(ctx.message.guild.roles, name='Human')
				if len(human.members) == 1:
					message_content += attacker_member.nick + ' attacks. Result: Critical Success'
					message_content += '\n' + 'Grabbed! But there is no-one else to hit...'
					first_attack_hit = 1
				else:
					other_humans = human.members
					other_humans.remove(attacker_member)
					unlucky_human = random.choice(other_humans)
					unlucky_row = np.where(player_database[:,0] == str(unlucky_human.id))
					if len(unlucky_row[0]) != 0:
						unlucky_data_index = unlucky_row[0][0]
						player_database[int(unlucky_data_index)][7] = str(int(player_database[int(unlucky_data_index)][7])-(self.class_damages[int(attacker_index)]+1))
						message_content += attacker_member.nick + ' attacks. Result: Critical Success'
						message_content += '\n' + 'Grabbed! ' + unlucky_human.mention + ' was hit by the attack instead!'
						first_attack_hit = 1
			else:
				defender_health = defender_health - (self.class_damages[int(attacker_index)]+1)
				message_content += attacker_member.nick + ' attacks. Result: Critical Success'
		elif result == 'Critical Fail':
			attacker_health = attacker_health - ceil(attacker_health/2)
			message_content += attacker_member.nick + ' attacks. Result: Critical Fail.'
		else:
			if self.class_fights[int(attacker_index)]+result >= self.class_fights[int(defender_index)]:
				if is_first_attack != None:
					human = discord.utils.get(ctx.message.guild.roles, name='Human')
					if len(human.members) == 1:
						message_content += attacker_member.nick + ' attacks. Result: ' + str(result) + '. Hit!'
						message_content += '\n' + 'Grabbed! But there is no-one else to hit...'
						first_attack_hit = 1
					else:
						other_humans = human.members
						other_humans.remove(attacker_member)
						unlucky_human = random.choice(other_humans)
						unlucky_row = np.where(player_database[:,0] == str(unlucky_human.id))
						if len(unlucky_row[0]) != 0:
							unlucky_data_index = unlucky_row[0][0]
							player_database[int(unlucky_data_index)][7] = str(int(player_database[int(unlucky_data_index)][7])-self.class_damages[int(attacker_index)])
							message_content += attacker_member.nick + ' attacks. Result: ' + str(result) + '. Hit!'
							message_content += '\n' + 'Grabbed! ' + unlucky_human.mention + ' was hit by the attack instead!'
							first_attack_hit = 1
				else:
					defender_health = defender_health - self.class_damages[int(attacker_index)]
					message_content += attacker_member.nick + ' attacks. Result: ' + str(result) + '. Hit!'
			else:
				message_content += attacker_member.nick + ' attacks. Result: ' + str(result) + '. Miss!'
		return attacker_health, defender_health, message_content, first_attack_hit

	def get_adjacent(self, ctx, center_member):
		human = discord.utils.get(ctx.message.guild.roles, name='Human')
		zombie = discord.utils.get(ctx.message.guild.roles, name='Zombie')
		if human in center_member.roles:
			member_list = sorted(human.members, key=lambda m: m.nick)
		elif zombie in center_member.roles:
			member_list = sorted(zombie.members, key=lambda m: m.nick)
		center_member_index = member_list.index(center_member)
		if center_member_index == len(member_list)-1:
			user_below = member_list[0]
		else:
			user_below = member_list[center_member_index+1]
		if center_member_index == 0:
			user_above = member_list[-1]
		else:
			user_above = member_list[center_member_index-1]
		return user_above, user_below

	def rng(self):
		bag = ['Critical Fail',-4,-4,-3,-3,-2,-2,-2,-1,-1,-1,0,0,0,1,1,1,2,2,2,3,3,4,4,'Critical Success']
		return random.choice(bag)

	# e-tagging for class based e-games
	@commands.command(brief='Attempt an e-tag.', description='.e_tag @human: Attempts to e-tag a user.')
	@commands.has_role('Zombie')
	async def e_tag(self, ctx, user: discord.Member):
		tag_commands = discord.utils.get(ctx.message.guild.text_channels,
					   name='tag-commands')
		if ctx.channel == tag_commands:
			tag_results = discord.utils.get(ctx.message.guild.text_channels,
						  name='tag-results')
			if discord.utils.get(user.roles, name='Human'):
				player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
				# Find zombie database entry and class
				zombie_data_index = self.find(player_database[:,0], str(ctx.message.author.id))
				if zombie_data_index:
					zombie_index = None
					zombie_health = None
					for role in ctx.message.author.roles:
						if role.name in self.class_list:
							zombie_index = self.class_list.index(role.name)
							zombie_health = int(player_database[int(zombie_data_index)][7])
							if zombie_index <= 3:
								await ctx.send('You need to select a zombie class!')
								return
							break
					if zombie_index == None:
						await ctx.send('Can\'t find your class. Have you chosen one?.')
						return
				else:
					await ctx.send('Could not find your player entry in database. Have you joined the game?')
					return
				# Find human database entry and class
				human_data_index = self.find(player_database[:,0], str(user.id))
				if human_data_index:
					human_index = None
					human_health = None
					for role in ctx.message.author.roles:
						if role.name in self.class_list:
							human_index = self.class_list.index(role.name)
							human_health = int(player_database[int(human_data_index)][7])
							break
					if human_index == None:
						await ctx.send('Can\'t find opponent\'s class. Have they chosen one?.')
						return
				else:
					await ctx.send('Could not find opponent entry in database. Have they joined the game?')
					return

				if zombie_health == 100 or zombie_health <= 0:
					await tag_results.send(ctx.message.author.mention + ' you have not performed a .refill command since you joined the game \ since you were last stunned \ since you were tagged. Please make sure you have done .refill anywhere and then re-attempt the e-tag.')
					return
				if human_health == 100 or human_health <= 0:
					await ctx.send(user.mention + ' has not performed a .refill command since they joined the game \ were revived. Please make sure they have done .refill anywhere and then re-attempt the e-tag.')
					await user.send('A zombie has attempted to tag you but you have not performed a .refill command since you joined the game \ were revived. Please make sure you do .refill in any channel as soon as possible.')
					return
				# Start the fight
				await user.send(ctx.message.author.nick + ' is attempting to tag you! go to #tag-results to see the fight!')
				message_content = '-------------------- \n' + ctx.message.author.mention + ' is attempting to tag ' + user.mention + '. Zombie Health: ' + str(zombie_health) + '. Human Health: ' + str(human_health) + '. \n'
				whose_turn = 'human' # Human Turn
				# heavy class functionality
				if discord.utils.get(user.roles, name='heavy'):
					whose_turn = 'zombie'
				# ranged class functionality
				if discord.utils.get(user.roles, name='ranged'):
					self.class_damages = [1,1,2,2,1,1,2,1]
					attacker = [user, human_index, human_health]
					defender = [ctx.message.author, zombie_index, zombie_health]
					result = self.rng()
					message_content += '\n'
					human_health, zombie_health, message_content, first_attack_hit = self.fight(ctx, attacker, defender, message_content, result)
					first_attack_hit = 0
					message_content += '\n'
					self.class_damages = [1,1,2,1,1,1,2,1]
				# fast class functionality
				if discord.utils.get(ctx.message.author.roles, name='fast'):
					whose_turn = 'zombie'
				# deflect class functionality
				if discord.utils.get(ctx.message.author.roles, name='deflect'):
					is_first_attack = 1
				else:
					is_first_attack = 0
				while zombie_health > 0 and human_health > 0:
					if whose_turn == 'human':
						attacker = [user, human_index, human_health]
						defender = [ctx.message.author, zombie_index, zombie_health]
						result = self.rng()
						# reroll class functionality
						if discord.utils.get(user.roles, name='reroll'):
							result2 = self.rng()
							if result == 'Critical Fail':
								result = result2
							elif result2 == 'Critical Fail':
								continue
							elif result == 'Critical Success' or result2 == 'Critical Success':
								result = 'Critical Success'
							elif result2 > result:
								result = result2
							else:
								continue
						# More deflect class functionality
						if is_first_attack == 1:
							human_health, zombie_health, message_content, first_attack_hit = self.fight(ctx, attacker, defender, message_content, result, is_first_attack)
							if first_attack_hit == 1:
								is_first_attack = 0

						else:
							human_health, zombie_health, message_content, first_attack_hit = self.fight(ctx, attacker, defender, message_content, result)
						await tag_results.send(message_content)
						message_content = ''
						whose_turn = 'zombie'
					elif whose_turn == 'zombie':
						attacker = [ctx.message.author, zombie_index, zombie_health]
						defender = [user, human_index, human_health]
						result = self.rng()
						zombie_health, human_health, message_content, first_attack_hit = self.fight(ctx, attacker, defender, message_content, result)
						await tag_results.send(message_content)
						message_content = ''
						whose_turn = 'human'
				if zombie_health <= 0:
					message_content += ctx.message.author.nick + ' has been stunned. They may not make any more tag attempts until the stun time has passed (please do .refill anywhere after that time to reset your health to full).'
					message_content += ' ' + user.nick + ' remaining health: ' + str(human_health) + '.'
					# collateral and splash class functionality
					if discord.utils.get(user.roles, name='collateral'):
						zombie = discord.utils.get(ctx.message.guild.roles, name='Zombie')
						if len(zombie.members) == 1:
							message_content += '\n Buckshot! But there is no-one else to hit...'
						elif len(zombie.members) == 2:
							other_zombies = zombie.members
							other_zombies.remove(ctx.message.author)
							other_zombie = random.choice(other_zombies)
							other_zombie_data_index = self.find(player_database[:,0], str(other_zombie.id))
							if other_zombie_data_index:
								player_database[int(other_zombie_data_index)][7] = str(int(player_database[int(other_zombie_data_index)][7])-1)
							message_content += '\n Buckshot! ' + other_zombie.mention + 'also took 1 damage.'
							if int(player_database[int(other_zombie_data_index)][7]) == 0:
								message_content += '\n' + other_zombie.mention + ' is now stunned.'
						else:
							adjacent1z, adjacent2z = self.get_adjacent(ctx, ctx.message.author)
							adjacent1z_data_index = self.find(player_database[:,0], str(adjacent1z.id))
							if adjacent1z_data_index:
								player_database[int(adjacent1z_data_index)][7] = str(int(player_database[int(adjacent1z_data_index)][7])-1)
							adjacent2z_data_index = self.find(player_database[:,0], str(adjacent2z.id))
							if adjacent2z_data_index:
								player_database[int(adjacent2z_data_index)][7] = str(int(player_database[int(adjacent2z_data_index)][7])-1)
							message_content += '\n Buckshot! ' + adjacent1z.mention + ' and ' + adjacent2z.mention + 'have also taken 1 damage.'
							if int(player_database[int(adjacent1z_data_index)][7]) == 0:
								message_content += '\n' + adjacent1z.mention + ' is now stunned.'
							if int(player_database[int(adjacent2z_data_index)][7]) == 0:
								message_content += '\n' + adjacent2z.mention + ' is now stunned.'
					if discord.utils.get(ctx.message.author.roles, name='splash'):
						does_spit = random.choice([True, False])
						if does_spit == True:
							human = discord.utils.get(ctx.message.guild.roles, name='Human')
							if len(human.members) == 1:
								message_content += '\n Splash Damage! But there is no-one else to hit...'
							elif len(human.members) == 2:
								other_humans = human.members
								other_humans.remove(user)
								other_human = random.choice(other_humans)
								other_human_data_index = self.find(player_database[:,0], str(other_human.id))
								if other_human_data_index:
									player_database[int(other_human_data_index)][7] = str(int(player_database[int(other_human_data_index)][7])-1)
								message_content += '\n Splash Damage! ' + other_human.mention + 'also took 1 damage.'
								if int(player_database[int(other_human_data_index)][7]) == 0:
									zombie_chat = discord.utils.get(ctx.message.guild.text_channels, name='zombie-chat')
									other_brain_code = str(player_database[int(other_human_data_index)][4])
									message_content += '\n' + other_human.mention + ' has now been tagged! ' + ctx.message.author.nick + ' please tag them with .tag ' + other_brain_code + ' in ' + zombie_chat.mention + '.'
							else:
								adjacent1h, adjacent2h = self.get_adjacent(ctx, user)
								adjacent1h_data_index = self.find(player_database[:,0], str(adjacent1h.id))
								if adjacent1h_data_index:
									player_database[int(adjacent1h_data_index)][7] = str(int(player_database[int(adjacent1h_data_index)][7])-1)
								adjacent2h_data_index = self.find(player_database[:,0], str(adjacent2h.id))
								if adjacent2h_data_index:
									player_database[int(adjacent2h_data_index)][7] = str(int(player_database[int(adjacent2h_data_index)][7])-1)
								message_content += '\n Splash Damage! ' + adjacent1h.mention + ' and ' + adjacent2h.mention + 'have also taken 1 damage.'
								if int(player_database[int(adjacent1h_data_index)][7]) == 0:
									zombie_chat = discord.utils.get(ctx.message.guild.text_channels, name='zombie-chat')
									human_brain_code = str(player_database[int(adjacent1h_data_index)][4])
									message_content += '\n' + other_human.mention + ' has now been tagged! ' + ctx.message.author.nick + ' please tag them with .tag ' + human_brain_code + ' in ' + zombie_chat.mention + '.'
								if int(player_database[int(adjacent2h_data_index)][7]) == 0:
									zombie_chat = discord.utils.get(ctx.message.guild.text_channels, name='zombie-chat')
									human_brain_code = str(player_database[int(adjacent2h_data_index)][4])
									message_content += '\n' + other_human.mention + ' has now been tagged! ' + ctx.message.author.nick + ' please tag them with .tag ' + human_brain_code + ' in ' + zombie_chat.mention + '.'
						else:
							message_content += '\n' + 'Spit failed to hit.'
					message_content +=  '\n --------------------'
				else:
					zombie_chat = discord.utils.get(ctx.message.guild.text_channels, name='zombie-chat')
					brain_code = str(player_database[int(human_data_index)][4])
					message_content += user.nick + ' has been tagged! ' + ctx.message.author.nick + ' please tag them with .tag ' + brain_code + ' in ' + zombie_chat.mention + '.'
					message_content += ' ' + ctx.message.author.nick + ' remaining health: ' + str(zombie_health) + '. \n --------------------'
				player_database[int(zombie_data_index)][7] = str(zombie_health)
				player_database[int(human_data_index)][7] = str(human_health)
				pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
				await tag_results.send(message_content)
			else:
				await ctx.send('User is not a Human.')

	@commands.command(brief='Attempt to shoot a zombie.', description='.potshot @user: Attempt to shoot a zombie.')
	@commands.has_role('Human')
	async def potshot(self, ctx, user: discord.Member):
		tag_commands = discord.utils.get(ctx.message.guild.text_channels,
					   name='tag-commands')
		if ctx.channel == tag_commands:
			tag_results = discord.utils.get(ctx.message.guild.text_channels, name='tag-results')
			if type(user) != discord.Member:
				await ctx.send('Please mention a user.')
			elif not discord.utils.get(user.roles, name='Zombie'):
				await ctx.send('Please mention a Zombie user.')
			else:
				player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
				human_data_index = self.find(player_database[:,0], str(ctx.message.author.id))
				if human_data_index:
					human_index = None
					human_health = None
					for role in ctx.message.author.roles:
						if role.name in self.class_list:
							human_index = self.class_list.index(role.name)
							human_health = int(player_database[int(human_data_index)][7])
							break
					if human_index == None:
						await ctx.send('Can\'t find your class. Have you chosen one?.')
						return
				else:
					await ctx.send('Could not find your player entry in database. Have you joined the game?')
					return
				zombie_data_index = self.find(player_database[:,0], str(user.id))
				if zombie_data_index:
					zombie_index = None
					zombie_health = None
					for role in user.roles:
						if role.name in self.class_list:
							zombie_index = self.class_list.index(role.name)
							zombie_health = int(player_database[int(zombie_data_index)][7])
							break
					if zombie_index == None:
						await ctx.send('Can\'t find your class. Have you chosen one?.')
						return
				else:
					await ctx.send('Could not find your player entry in database. Have you joined the game?')
					return
				message_content = '-------------------- \n' + ctx.message.author.mention + ' is attempting to shoot ' + user.mention + '. Human Health: ' + str(human_health) + '. Zombie Health: ' + str(zombie_health) + '. \n'
				result = self.rng()
				if result == 'Critical Success':
					zombie_health = zombie_health - 2
					message_content += ctx.message.author.nick + ' attacks. Result: Critical Success'
				elif result == 'Critical Fail':
					human_health = human_health - ceil(human_health/2)
					message_content += ctx.message.author.nick + ' attacks. Result: Critical Fail.'
				elif self.class_fights[int(human_index)]+result >= self.class_fights[int(zombie_index)]:
					zombie_health = zombie_health - 1
					message_content += ctx.message.author.nick + ' attacks. Result: ' + str(result) + '. Hit!'
				else:
					message_content += ctx.message.author.nick + ' attacks. Result: ' + str(result) + '. Miss!'
				message_content += '\n'
				if human_health <= 0:
					zombie_chat = discord.utils.get(ctx.message.guild.text_channels, name='zombie-chat')
					brain_code = str(player_database[int(human_data_index)][4])
					message_content += ctx.message.author.nick + ' has been tagged! ' + user.nick + ' please tag them with .tag ' + brain_code + ' in ' + zombie_chat.mention + '.'
					message_content += ' ' + user.nick + ' remaining health: ' + str(zombie_health) + '. \n --------------------'
				elif zombie_health <= 0:
					message_content += user.nick + ' has been stunned. They may not make any more tag attempts until the stun time has passed (please do .refill anywhere after that time to reset your health to full).'
					message_content += ' ' + ctx.message.author.nick + ' remaining health: ' + str(human_health) + '. \n --------------------'
				else:
					message_content += ' ' + ctx.message.author.nick + ' remaining health: ' + str(human_health) + '. \n'
					message_content += ' ' + user.nick + ' remaining health: ' + str(zombie_health) + '. \n --------------------'
				player_database[int(human_data_index)][7] = str(human_health)
				player_database[int(zombie_data_index)][7] = str(zombie_health)
				pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
				await tag_results.send(message_content)

	@commands.command(brief='Reset your health', description='.refill: Reset your health to your classes\' starting health value.')
	async def refill(self, ctx):
		user_id = ctx.message.author.id
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		player_index = self.find(player_database[:,0], str(ctx.message.author.id))
		if not player_index:
			await ctx.send('Player not found.')
			return
		for role in ctx.message.author.roles:
			if role.name in self.class_list:
				class_index = self.class_list.index(role.name)
				break
		player_database[int(player_index)][7] = str(self.class_healths[int(class_index)])
		pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
		await ctx.message.author.send('Your current health is: ' + player_database[int(player_index)][7] + '.')

	@commands.command(brief='Heal yourself for an ammount', description='.heal [ammount]: Heals user for ammount.')
	async def heal(self, ctx, heal_ammount):
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		player_index = self.find(player_database[:,0], str(ctx.message.author.id))
		if not player_index:
			return

		for role in ctx.message.author.roles:
			if role.name in self.class_list:
				player_class_index = self.class_list.index(role.name)
				break
		if player_class_index == None:
			await ctx.send('Can\'t find your class. Have you chosen one?.')
			return

		new_health = int(player_database[int(player_index)][7]) + int(heal_ammount)
		if new_health > self.class_healths[int(player_class_index)]:
			new_health = self.class_healths[int(player_class_index)]
		player_database[int(player_index)][7] = str(new_health)

		pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
		await ctx.message.author.send('You have been healed! Your current health is: ' + player_database[int(player_index)][7] + '.')
		await ctx.send('Player Healed.')

	@commands.command(brief='Take an ammount of damage', description='.take_damage [damage]: Reduce your health by the damage value.')
	async def take_damage(self, ctx, damage):
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		player_index = self.find(player_database[:,0], str(ctx.message.author.id))
		if not player_index:
			return

		new_health = int(player_database[int(player_index)][7]) - int(damage)
		if new_health <= 0:
			new_health = 0
		player_database[int(player_index)][7] = str(new_health)
		pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
		if new_health <= 0:
			await ctx.send('You are dead. If you are a Human, give your braincode to the zombie that killed you. If you are a zombie, you are out for the current respawn time. Use .refill after that time to refill your health.')
		else:
			await ctx.message.author.send('Your current health is: ' + str(new_health) + '.')
			await ctx.send('Damage dealt.')

	@commands.command(brief='Announce tag resets every hour from now, X times', description='.tag_reset [times to post]: Announce tag resets every hour from now, X times')
	@commands.has_role('Moderator')
	async def tag_reset(self, ctx, times_to_post):
		game_announcements = discord.utils.get(ctx.message.guild.text_channels,
							   name='game-announcements')

		human = discord.utils.get(ctx.message.guild.roles, name='Human')
		zombie = discord.utils.get(ctx.message.guild.roles, name='Zombie')
		for i in range(int(times_to_post)):
			await game_announcements.send(human.mention + ' ' + zombie.mention + ' - Zombie tag attempts reset to two!')
			await asyncio.sleep(3600)

	# explode class functionality
	@commands.command(brief='Activate the explode class ability', description='.explode: Activate the explode class ability.')
	@commands.has_role('explode')
	async def explode(self, ctx):
		game_announcements = discord.utils.get(ctx.message.guild.text_channels,
							   name='game-announcements')
		zombie =  discord.utils.get(ctx.message.guild.roles, name='Zombie')
		human =  discord.utils.get(ctx.message.guild.roles, name='Human')
		await game_announcements.send(human.mention + zombie.mention + ' - Explosion! For the next five minutes, zombies get +1 to fight and -1 to health.')
		self.class_fights = [4,3,5,4,5,5,4,5]
		self.class_healths = [6,5,3,5,2,3,3,3]
		await asyncio.sleep(300)
		self.class_fights = [4,3,5,4,4,4,3,4]
		self.class_healths = [6,5,3,5,3,4,4,4]

	@commands.command(brief='Refill all Zombies', description='.refill_zombies: Refill all Zombies.')
	@commands.has_role('Moderator')
	async def refill_zombies(self, ctx):
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		zombie = discord.utils.get(ctx.message.guild.roles, name='Zombie')
		for user in zombie.members:
			player_index = self.find(player_database[:,0], str(user.id))
			if player_index:
				for role in user.roles:
					if role.name in self.class_list:
						class_index = self.class_list.index(role.name)
						break
				player_database[int(player_index)][7] = str(self.class_healths[int(class_index)])
		pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
		zombie_chat = discord.utils.get(ctx.message.guild.text_channels,
						   name='zombie-chat')
		await zombie_chat.send('All zombies refilled!')

	@commands.command(brief='Refill all Humans', description='.refill_zombies: Refill all Humans.')
	@commands.has_role('Moderator')
	async def refill_humans(self, ctx):
		player_database = np.loadtxt(self.databasepath, dtype=str, delimiter=',')
		human = discord.utils.get(ctx.message.guild.roles, name='Human')
		for user in human.members:
			player_index = self.find(player_database[:,0], str(user.id))
			if player_index:
				for role in user.roles:
					if role.name in self.class_list:
						class_index = self.class_list.index(role.name)
						break
				player_database[int(player_index)][7] = str(self.class_healths[int(class_index)])
		pd.DataFrame(player_database).to_csv(self.databasepath, header=None, index=None)
		human_chat = discord.utils.get(ctx.message.guild.text_channels,
						   name='human-chat')
		await human_chat.send('All humans refilled!')

def setup(bot):
	bot.add_cog(EHvZCommands(bot))
