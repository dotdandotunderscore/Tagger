# Various old types of e_tagging

	# @commands.command(brief='Attempt an e-tag.', description='.e_tag @user or .e_tag @zombie @human: Attempts to e-tag a user, with help if a Zombie is mentioned.')
	# @commands.has_role('Zombie')
	# async def e_tag(self, ctx, users: commands.Greedy[discord.Member] = None):
	# 	tag_commands = discord.utils.get(ctx.message.guild.text_channels, name='tag-commands')
	# 	# Checks if .tag was run in zombie-chat
	# 	if ctx.channel == tag_commands:
	# 		tag_attempts = discord.utils.get(ctx.message.guild.text_channels, name='tag-attempts')
	# 		stun_attempts = discord.utils.get(ctx.message.guild.text_channels, name='stun-attempts')
	# 		human = discord.utils.get(ctx.message.guild.roles, name='Human')
	# 		zombie = discord.utils.get(ctx.message.guild.roles, name='Zombie')
	# 		if len(users) == 1:
	# 			if human in users[0].roles:
	# 				await ctx.message.delete()
	# 				await tag_attempts.send(ctx.message.author.mention + ' is attempting to tag ' + users[0].mention +
	# 				'. Post your stun attempt in ' + stun_attempts.mention + '.')
	# 			else:
	# 				await ctx.send('User is not a Human.')
	# 		if len(users) == 2:
	# 			if zombie in users[0].roles:
	# 				if human in users[1].roles:
	# 					await ctx.message.delete()
	# 					await tag_attempts.send(ctx.message.author.mention + ' and ' + users[0].mention + ' are attempting to tag '
	# 					+ users[1].mention + '. Post your stun attempt in ' + stun_attempts.mention +
	# 					'. You must hit at least 2 of your shots.')
	# 				else:
	# 					await ctx.send('User is not a Human.')
	# 			else:
	# 				await ctx.send('Your co-tagger is not a Zombie.')
	#
	# @commands.command(brief='Attempt an e-tag.', description='.e_tag @user or .e_tag @human: Attempts to e-tag a user.')
	# @commands.has_role('Zombie')
	# async def e_tag(self, ctx, user: commands.Greedy[discord.Member] = None):
	# 	tag_commands = discord.utils.get(ctx.message.guild.text_channels,
	# 				   name='tag-commands')
	# 	if ctx.channel == tag_commands:
	# 		tag_results = discord.utils.get(ctx.message.guild.text_channels,
	# 					  name='tag-results')
	# 		human = discord.utils.get(ctx.message.guild.roles, name='Human')
	# 		zombie = discord.utils.get(ctx.message.guild.roles, name='Zombie')
	# 		if len(users) == 1:
	# 			if human in users[0].roles:
	# 				message_content = ctx.message.author.mention + ' is attempting to tag ' + users[0].mention + '.')
	# 				fight = await tag_results.send(message_content)
	# 			else:
	# 				await ctx.send('User is not a Human.')
	# 		else:
	# 			await ctx.send("Please only mention one user at a time.")
	# @commands.command(brief='Attempt an OZ e-tag.', description='.oz_e_tag @user: Attempts to OZ e-tag a user.')
	# @commands.has_role('Moderator')
	# async def oz_e_tag(self, ctx, user: commands.Greedy[discord.Member] = None):
	# 	tag_commands = discord.utils.get(ctx.message.guild.text_channels, name='tag-commands')
	# 	# Checks if .tag was run in zombie-chat
	# 	if ctx.channel == tag_commands:
	# 		tag_attempts = discord.utils.get(ctx.message.guild.text_channels, name='tag-attempts')
	# 		stun_attempts = discord.utils.get(ctx.message.guild.text_channels, name='stun-attempts')
	# 		human = discord.utils.get(ctx.message.guild.roles, name='Human')
	# 		if human in users[0].roles:
	# 			await ctx.message.delete()
	# 			await tag_attempts.send('An OZ is attempting to tag ' + users[0].mention +
	# 			'. Post your stun attempt in ' + stun_attempts.mention + '.')
