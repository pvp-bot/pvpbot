# pvpbot.py

import discord # discord bot
import sys

import builds
from secrets import bot_token

# 'constants'
channel_name = 'build-discussion'
# channel_name = 'test-chan'

# bot commands
bot_ignore = '!i'

client = discord.Client()


async def dlAll():
	channels = client.get_all_channels()
	counter = 0	
	for chan in channels:
		if str(chan.type) == 'text' and chan.name == channel_name:
			csv_data = []
			messages = await chan.history(limit=None).flatten()
			for message in messages:
				counter = counter + 1
				if builds.build_url in message.content: # if message contains a build
					builds.parseURL(message,False)
				elif len(message.attachments) > 0: #if message has an attachment
					for a in message.attachments:
						if a.filename.endswith(builds.build_suf):
							builds.parseAttach(message,a.url,False)
							break
	print(str(counter) + ' messages read')



# on bot connect
@client.event
async def on_ready():
	print('logged in as {0.user}'.format(client))
	if len(sys.argv) > 1 and sys.argv[1] == '--dl-all':
		await dlAll()
		return



@client.event
async def on_message(message):
	# ignore messages from ourself
	msg_author = message.author
	if msg_author == client.user:
		return

	# if not bot_ignore in message.content and correct channel:
	if str(message.channel) == channel_name and not bot_ignore in message.content:
		if builds.build_url in message.content: # if message contains a build
			builds.parseURL(message,True)

		elif len(message.attachments) > 0: #if message has an attachment
			for a in message.attachments:
				if a.filename.endswith(builds.build_suf):
					builds.parseAttach(message,a.url,True)
					break
		# bot messages		
		else:
			# no build in message
			if '!link' in message.content:
				await message.channel.send('<http://bit.do/pvpbuilds>')
				# RARE await message.channel.send(message.author.mention+' <https://docs.google.com/spreadsheets/d/'+secrets.sheets_id+'/edit#gid='+secrets.sheets_num+'>')
			# elif '!kickball' in message.content:
			# 	await message.channel.send('kickball weds and sat nights @ 6 pm pacific, check out the link for rules and more info \n<https://forums.homecomingservers.com/topic/1492-weekly-kickball-thread/>')
			elif '!pvpbot' in message.content:
				await message.channel.send('hi '+message.author.mention+', I parse builds posted here and add them to a spreadsheet\n**!link** to link spreadsheet\ninclude **!i** in your message to ignore adding a build to the spreadsheet' )
			

		

client.run(bot_token) # Add bot token here