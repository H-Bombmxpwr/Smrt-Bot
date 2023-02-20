import discord
from discord.ext import commands, tasks
import os
from functionality.keep_alive import keep_alive
from storage.Lists_Storage import thedan, days, status, friday
from cogs.help import NewHelpName
import time
from functionality.functions import check_carrot
import json
from functionality.trie import Trie
from itertools import cycle
import asyncio
from discord.ui import Button,View


def get_prefix(client, message):  #grab server prefix
    with open("storage/prefixes.json", "r") as f:
        prefixes = json.load(f)
      
    return prefixes[str(message.guild.id)]



client = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())
client.help_command = NewHelpName()
client.synced = True
status_i = cycle(status)

trie = Trie()
table = {
    "\"": None,
    "'": None,
    "-": None,
    "`": None,
    "~": None,
    ",": None,
    ".": None,
    ":": None,
    ";": None,
    "_": None
}


def buildTrie():
    file = open("storage/words.txt", 'r')

    for line in file:
        line = line.strip()
        trie.insert(line)
    file.close()
    return True


@client.event
async def on_command_error(ctx, error):  #detects if a command is valid
    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(
            title=f"Error",
            description=f"Command \'" + ctx.message.content +
            "   \' not found. \nUse `list: ` or `help: ` for a list of commands",
            color=0xff0000)
        await ctx.send(embed=em)


@client.event
async def on_ready():
    print('=------------------------------=')
    print("Rate Limited = " + str(client.is_ws_ratelimited()))
    change_status.start()
    built = False
    #built = buildTrie()
    if built:
        print("Trie is built. Profanity filter is on.\n")
    else:
        print("Trie was not built, profanity filter is off\n")

    print('{0.user} is online'.format(client))
    print('=------------------------------=')


@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name=next(status_i)))


@client.event
async def on_guild_join(guild):  #add default prefix to the json file
    with open("storage/prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "$"

    with open("storage/prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):  #remove prefix if bot is kicked
    with open("storage/prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open("storage/prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text = message.content.lower()
    text = text.translate(str.maketrans(table))
    author_id = message.author.id
    time_zone = -6
    mod_time = int((int(time.time()) + (time_zone * 3600)) / 86400) % 7

    #sends the prefix if the useer forgets what it is
    if text == "prefix":
        await message.channel.send("This server's prefix is `" +
                                   str(get_prefix(client, message)) + "`")

    #profanity filter
    #if author_id != 239605426033786881:
    #    isClean = True
    #    message_word_list = text.split()
    #    for word in message_word_list:
    #        if trie.search(word):
    #            isClean = False
    #            break
    #    if not isClean:
    #        await message.add_reaction("😮")

    # thursday!!!
    if any(word in text for word in days):

        if mod_time == 0:
            button = Button(label = "isitthursday.org", style = discord.ButtonStyle.primary, url = "http://isitthursday.org/")
            view = View()
            view.add_item(button)
            await message.channel.send("Happy Thursday!", view=view)
           
        else:
            await message.add_reaction("❌")

    #the dan
    if any(word in text for word in thedan):
        await message.reply("I LOVE STEELY DAN!")

    #flat fuck friday
    if any(word in text for word in friday):

        if  mod_time == 1:
            await message.add_reaction("🐊")
            embedVar = discord.Embed(title = "FLAT FUCK FRIDAY", description = "Happy Flat Fuck Friday", color = 0x7A7A58).set_image(url = "https://images-ext-1.discordapp.net/external/Aj38ONNQjynkVNpJml4oDYHT7M3BbwQRYmGPN2vc_40/https/i.kym-cdn.com/entries/icons/original/000/037/038/fffcover.jpg?width=1177&height=662")
            await message.channel.send(embed=embedVar)
        else:
            await message.add_reaction("❌")

    
    #milkie monday
    if any(word in text for word in ["milkie monday", "milkiemonday","milky monday","milkymonday"]):
      

      if mod_time == 4:
        await message.add_reaction("🥛")
      else:
        await message.add_reaction("❌")

    #no clothes tuesday
    if any(word in text for word in ["no clothes tuesday","noclothestuesday"]):
      time_zone = -6

      if int((int(time.time()) + (time_zone * 3600)) / 86400) % 7 == 5:
        await message.add_reaction("🧦")
      else:
        await message.add_reaction("❌")

    #Carrot agree function
    if check_carrot(text,message) == 1:
     await message.channel.send(message.content + '^')

    await client.process_commands(message)


async def main():
    async with client:
        await client.load_extension('cogs.music')
        await client.load_extension('cogs.services')
        await client.load_extension('cogs.mod')
        await client.load_extension('cogs.games')
        await client.load_extension('cogs.help')
        await client.load_extension('cogs.flight')
        await client.start(os.getenv('token'))


keep_alive()
asyncio.run(main())