# builds.py
import urllib # grabbing .mxd files
import requests
import gsheet
import zlib # decompressing hex
import re
import csv
import json

# bot_tag = "!t "
build_url = "http://www.cohplanner.com/mids/download.php" # to match in comments
build_suf = ".mxd" # to match in attachments

at_icons = {
	'Blaster'		:'https://i.imgur.com/hNCbfBk.png',
	'Controller'	:'https://i.imgur.com/DKYvaYY.png',
	'Defender'		:'https://i.imgur.com/T1Quw8q.png',
	'Scrapper'		:'https://i.imgur.com/3xSXKsP.png',
	'Tanker'		:'https://i.imgur.com/Qt6XXqt.png',
	'Brute'			:'https://i.imgur.com/BXgorAg.png',
	'Corruptor'		:'https://i.imgur.com/0VmuUQP.png',
	'Dominator'		:'https://i.imgur.com/3toE2aG.png',
	'Mastermind'	:'https://i.imgur.com/VYxhTHG.png',
	'Stalker'		:'https://i.imgur.com/U4o1PRm.png',
	'Sentinel'		:'https://i.imgur.com/ew9W901.png',
	'Peacebringer'	:'https://i.imgur.com/THAzwT5.png',
	'Warshade'		:'https://i.imgur.com/X1a4CZ4.png',
	'Arachnos Widow':'https://i.imgur.com/z52YbEI.png',
	'Arachnos Soldier':'https://i.imgur.com/6gfIqT6.png'
}

aliases_at = {
	'mm':'Mastermind',
	'ws':'Warshade',
	'crab':'Soldier'
}
aliases_pow = {
	'ss':'Super',
	'sj':'Street',
	# 'ea':'Energy Aura', 
	'wp':'Willpower', 
	# 'em':'Energy Melee'
	'ff':'Force Field',
	# 'ta':'Trick',
	'dev':'Gadgets',
	'device':'Gadgets',
	'devices':'Gadgets',
}

# change request header so Discord doesn't 403 the urlrequests
opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)

# parse hexstring into AT, primary, secondary
def parseHex(hexstring):
	hexbytes = bytearray.fromhex(hexstring)
	hexd = str(zlib.decompress(hexbytes))
	# print(hexd)
	at1 = hexd.split("Class_")
	at2 = at1[1].split("\\")
	at = at2[0]
	
	pri = ''
	sec = ''
	if at == 'Arachnos_Widow':
		at  = 'Arachnos Widow'
		pri = 'Fortunata Training'
		sec = 'Fortunata Teamwork'
	elif at == 'Arachnos_Soldier':
		at  = 'Arachnos Soldier'
		pri = 'Bane Spider Soldier'	
		sec = 'Bane Spider Training'
	else:
		pri1 = at1[1].split(at+'_')
		pri2 = pri1[1].split('.')
		# if 'Template' in pri1[2]:
		# 	pri2 = pri1[3].split('.')
		pri = pri2[1].split('\\')[0].replace('_',' ')
		pri = re.sub(r'[^\w ]', '', pri) # removed irreg non-alpha chars
		
		sec1 = pri1[2].split('.')
		sec = sec1[1].split('\\')[0].replace('_',' ')
		sec = re.sub(r'[^\w ]', '', sec)
	if pri == 'Brawling':
		pri = 'Street Justice'
	if sec == 'Brawling':
		sec = 'Street Justice'
	if pri == 'Quills':
		pri = 'Spines'
	print(at + ', ' + pri + ', ' + sec)

	data = [at,pri,sec]

	return data


def parseTag(content): # not implemented yet
	tag1 = split(bot_tag)
	tag2 = tag1[1].split()
	tag  = tag2[0] 
	if len(tag) > 16:
		tag = ''


def addBuild(message,parsed,url,hexstring,add):
	if not add or not gsheet.findHex(hexstring): # if we're not adding to spreadsheet OR if it's not a duplicate
		# tag = ''
		# if bot_tag in message.content:
		# 	tag = parseTag(message.content)

		msg_link = message.jump_url
		msg_time = str(message.created_at)
		author_id = str(message.author)
		msg_author = author_id.split('#')[0]
		try:
			if message.author.nick:
				msg_author = message.author.nick
		except:
			pass
			

		entry =	[[msg_author,msg_time,parsed[0],parsed[1],parsed[2],
				'=HYPERLINK(L10,"download")','="from:"&J10&" during:"&LEFT(B10,10)&" has:"&(IF(ISNUMBER(FIND("cohplanner",L10)),"link","file"))','=HYPERLINK(M10,"msg link")',
				'0',author_id,'', # rating, userID, repeat
				url,msg_link,hexstring]]
		if add:
			gsheet.add(entry)
		else:
			with open('dlAll.csv', 'a') as f:
				writer = csv.writer(f)
				writer.writerow(entry[0])


def parseURL(message,add,hexonly=False):
	hs1 = message.content.split(build_url)
	hs2 = hs1[1].split('&dc=')
	hs3 = hs2[1].split()
	hexstring = hs3[0] # parse out the hex string from the url

	if hexonly:
		return hexstring
	url = build_url + hs2[0] + '&dc=' + hexstring
	parsed = parseHex(hexstring)
	addBuild(message,parsed,url,hexstring,add) 


def parseAttach(message,url,add,hexonly=False):
	data1 = str(urllib.request.urlopen(url).read())
	# if in uncompressed format
	if '\\n' in data1 or '\\r\\n' in data1:
		data2 = data1.split('HEX')
		data3 = data2[1].replace('|\\r\\n|','')[1:]
		data3 = data3.replace('|\\n|','')
		hexstring = data3.split('-')[0]
	# if in compressed format
	else:
		data2 = data1.split('||')
		data3 = data2[1].split('|')
		hexstring = data3[0]
	if hexonly:
		return hexstring
	parsed = parseHex(hexstring)
	addBuild(message,parsed,url,hexstring,add)

def parseAliases(at,pri,sec):
	if at in aliases_at:	
		at = aliases_at[at]
	if pri in aliases_pow:
		pri = aliases_pow[pri]
	if sec in aliases_pow:
		sec = aliases_pow[sec]
	return [at,pri,sec]

def parseSearch(message,rated):
	search_split = '!search '
	if not rated:
		search_split = '!searchall '
	parse = message.split(search_split)[1].split()

	if len(parse) == 0:
		return False
	elif len(parse) == 1: # only searching for AT
		parse.append('')
		parse.append('')
	elif len(parse) == 2: # only searching for primary
		parse.append('')

	for i in range(len(parse)):
		if parse[i] == '*': # i.e. blank in search
			parse[i] = ''

	# aliases
	parse = parseAliases(parse[0],parse[1],parse[2])


	print('search string: ' + parse[0] + ', '+ parse[1] + ', '+ parse[2])
	embed_content = gsheet.findBuild(parse[0].lower(),parse[1].lower(),parse[2].lower(),rated)
	if embed_content:
		embed_content['at_icon'] = at_icons[embed_content['at']]
		return embed_content
	return False

def parseVote(message):
	msg_time = str(message.created_at)
	vote_count = 0
	reactions = message.reactions
	for r in reactions:
		if str(r.emoji) == '💯':
			vote_count = r.count
			break
	gsheet.updateVote(msg_time,vote_count)


def buildPop(url,filename):
	mxd = urllib.request.urlopen(url)

	if not 'Mids' in str(mxd.read().decode('utf8')):
		return False
	with open('enh.json') as e:
		data = json.load(e)
		
		string1 = '' # first 70
		string2 = '' # remainder
		
		mxd = urllib.request.urlopen(url)
		line = str(mxd.readline().decode('utf8'))
		while not '------------' in line:
			line = str(mxd.readline().decode('utf8'))
		line = str(mxd.readline().decode('utf8'))
		count = 0
		while not '------------' in line:
			split = line.split("\t")[-1]
			split = re.sub(r'\([^)]*\)', '', split)
			split = re.sub(r'\n', '', split)
			split = re.sub(r'\r', '', split)

			split = split.split(', ')
			
			for i in split:
				if i != '' and i != 'Empty':
					if count<70:
						string1 = string1 + '$$boost '+data[i]['UID']+' '+data[i]['UID']+' '+'50' #str(data[i]['LevelMax'])
					else:
						string2 = string2 + '$$boost '+data[i]['UID']+' '+data[i]['UID']+' '+'50' #str(data[i]['LevelMax'])
					count = count + 1
			line = str(mxd.readline().decode('utf8'))
		print(str(count)+' enhancements total')

		with open('mxd.mnu',mode='w') as menu:
			menu.write('//POPMENU generated from Mids .mxd file by @pvpbot on Homecoming PVP Discord\n')
			menu.write('Menu "mxd"\n')
			menu.write('{\n')
			menu.write('\tTitle "'+filename+'"\n')
			menu.write('\tOption "1 - Level up" "levelup_xp 50$$influence_add 1000000000"\n')
			menu.write('\tOption "2 - Unlock badges/patron/incarnates" "badge_grant FreedomPhalanxSet$$badge_grant DimensionalHopperSet$$badge_grant AtlasSet$$badge_grant TaskForceCommander$$badge_grant MagusSet$$badge_grant CreySet$$badge_grant GeasoftheKindOnes$$badge_grant RiktiWarSet$$badge_grant RIWEAccolade$$badge_grant MiragePatron$$badge_grant IncarnateAlphaSlot$$badge_grant IncarnateJudgementSlot$$badge_grant IncarnateInterfaceSlot$$badge_grant IncarnateLoreSlot$$badge_grant IncarnateDestinySlot$$badge_grant IncarnateHybridSlot$$badge_grant OuroborosEnabled"\n')
			menu.write('\tOption "3 - Slot first 70 enhancements" "'+string1+'"\n')
			menu.write('\tOption "4 - Slot remaining enhancements" "'+string2+'"\n')
			menu.write('\tLockedOption\n')
			menu.write('\t{\n')
			menu.write('\t\tDisplayName "Reminder to get your incarnates, boosters"\n')
			menu.write('\t\tBadge "X"\n')
			menu.write('\t}\n')
			menu.write('}')
		return True
