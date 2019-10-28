# pvpbot.py

import discord # discord bot
import sys

import builds
import secrets


# bot commands
bot_ignore = '!i'
bot_builds = '!builds'

client = discord.Client()

# dl all builds from most recent, number is how many mesgs to parse.
async def dlAll(dl_num=None):
	if dl_num:
		dl_num = int(dl_num)
	channels = client.get_all_channels()
	counter = 0	
	for chan in channels:
		if str(chan.type) == 'text' and chan.name == secrets.channel_name:
			csv_data = []
			messages = await chan.history(limit=dl_num).flatten()
			for message in messages:
				counter = counter + 1
				if not bot_ignore in message.content:
					if builds.build_url in message.content: # if message contains a build
						builds.parseURL(message,False)
					elif len(message.attachments) > 0: #if message has an attachment
						for a in message.attachments:
							if a.filename.endswith(builds.build_suf):
								builds.parseAttach(message,a.url,False)
								break
	print(str(counter) + ' messages read')
	sys.exit(0)
	return



# on bot connect
@client.event
async def on_ready():
	print('logged in as {0.user}'.format(client))
	arg_len = len(sys.argv)
	if arg_len > 1 and sys.argv[1] == '--dl-all':
		dl_num = None
		dl_flag = False
		if arg_len > 2:
			dl_num = sys.argv[2]
		await dlAll(dl_num)	
		return

def buildEmbed(match):
	desc = "posted by " + match['author'] + " [" + match['comment_time'] + "](" + match['comment_url'] + ")"
	# desc = desc + "\nfound in the [pvp discord build spreadsheet](https://docs.google.com/spreadsheets/d/1FNejy_CHV4Khr9dy3m7wn8-J0OARwrSbHcKmkBRuG1Y/edit#gid=0)"
	auth = match['pri'] + "/" + match['sec'] + " " + match['at']
	if match['at'] == 'Peacebringer' or match['at'] == 'Warshade' or match['at'] == 'Arachnos Soldier' or match['at'] == 'Arachnos Widow':
		auth = match['at']
	build_embed = discord.Embed(url=match['build_url'], description=desc)
	build_embed.set_author(name=auth, url=match['build_url'], icon_url=match['at_icon'])
	return build_embed

@client.event
async def on_message(message):
	# ignore messages from ourself
	msg_author = message.author
	if msg_author == client.user: # or str(msg_author) == 'Fire Wire#1104' # ;)
		return

	# if not bot_ignore in message.content and correct channel:
	if str(message.channel) == secrets.channel_name and not bot_ignore in message.content:
		if builds.build_url in message.content: # if message contains a build
			builds.parseURL(message,True)

		elif len(message.attachments) > 0: #if message has an attachment
			for a in message.attachments:
				if a.filename.endswith(builds.build_suf):
					builds.parseAttach(message,a.url,True)
					break
		
		# bot messages		
		else: # no build in message
			
			# link to spreadsheet
			if '!builds' in message.content:
				await message.channel.send(message.author.mention+' <http://bit.do/pvpbuilds>')
			
			# find matching build
			elif message.content.startswith('!search ') or message.content.startswith('!searchall '):
				rated = True
				if message.content.startswith('!searchall '):
					rated = False
				match = builds.parseSearch(message.content, rated)
				if not match == False:
					await message.channel.send(embed=buildEmbed(match))
				print('')
				return
			
			## not in use		
			# elif '!kickball' in message.content:
			# 	await message.channel.send('kickball weds and sat nights @ 6 pm pacific, check out the link for rules and more info \n<https://forums.homecomingservers.com/topic/1492-weekly-kickball-thread/>')
	
	# DM bot directly
	elif str(message.channel.type) == 'private':
		print(str(message.channel.recipient)+': '+message.content)
		if message.content.startswith('!search ') or message.content.startswith('!searchall '):
			rated = True
			if message.content.startswith('!searchall '):
				rated = False
			match = builds.parseSearch(message.content, rated)
			if not match == False:
				await message.channel.send(embed=buildEmbed(match))
		elif '!builds' in message.content:
			await message.channel.send(message.author.mention+' <http://bit.do/pvpbuilds>')
		print('')
		return

		

@client.event
async def on_raw_reaction_add(payload):
	if payload.emoji.name == '💯':
		for chan in client.get_all_channels():
			if str(chan) == secrets.channel_name:
				try:
					msg = await chan.fetch_message(payload.message_id)
					builds.parseVote(msg)
				except:
					continue

@client.event
async def on_raw_reaction_remove(payload):
	if payload.emoji.name == '💯':
		for chan in client.get_all_channels():
			if str(chan) == secrets.channel_name:
				try:
					msg = await chan.fetch_message(payload.message_id)
					builds.parseVote(msg)
				except:
					continue


client.run(secrets.bot_token)