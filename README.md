
![](https://i.imgur.com/MsvccZG.png)

**repo migrated to https://github.com/pvp-bot/pvpbot**

**requirements**  
python3, [google python api](https://developers.google.com/sheets/api/quickstart/python#step_2_install_the_google_client_library), discord.[]()py, [a discord bot account](https://discordpy.readthedocs.io/en/latest/discord.html)

**setup**  
follow the linked google page to setup that stuff
follow the discord instructions for setting up a bot
create a secrets.py file and add your spreadsheet info and discord bot token  
*channel_name , bot_token, sheets_id, sheets_num*  
edit the spreadsheet range strings in gsheet.py

**running**  
`python pvpbot.py` to run normally
`python pvpbot.py --dl-all x` parse the last x messages in a channel and add those builds to a .csv file, parses entire channel history if no number given. exit on completion

**commands**  
*!builds* - returns a link to the spreadsheet  
*!search <at> <primary> <secondary>* - searches the spreadsheet the highest voted, most recent matching build. 1-word inputs for each field, matches substring (e.g. *def* in *def*ender)  
*!searchall* - to ignore votes  
votes are by 💯 reactions on build posts
  
the enh.json has been formatted from the enhancement database from [Mids](https://github.com/ImaginaryDevelopment/imaginary-hero-designer)

