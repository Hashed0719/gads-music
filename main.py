import discord 
from discord.ext import commands

import os

import lavalink_server

import alive

REPLIT = False
LAVALINK_SERVER_LOCAL = False   #literals in music.py must be changed in create node
BOT_PREFIX = "m."


#instantiating Bot
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(BOT_PREFIX),
    intents = discord.Intents.all()
)


@bot.event
async def on_ready():   #bot client
    print(f"connected as {bot.user}")

@bot.event              #sends prefix in dc chat
async def on_message(msg :discord.Message):
    if msg.author == bot.user:
        return 
    if "prefix" in msg.content:
        prefix = await bot.get_prefix(msg)
        await msg.channel.send(f"Hello There! my prefix is {prefix}")
    await bot.process_commands(msg)

# #starting lavalink
if LAVALINK_SERVER_LOCAL:
    HOST = lavalink_server.HOST
    PORT = lavalink_server.PORT

    if lavalink_server.port_in_use(HOST, PORT):
        print("Skipping server start!")
    else:
        lavalink_server.start()
        lavalink_server.wait_until_running()


#adding cogs
extensions = [
    "cogs._initManager",
    "cogs.general",
    "cogs.music"
]

[bot.load_extension(name) for name in extensions]


#running bot
if REPLIT:
    token = os.environ["token"]
    alive.keep_alive()
else:
    import dotenv
    dotenv.load_dotenv()
    token = os.getenv("token")

bot.run(token)