import discord 
from discord.ext import commands


class general_cog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

def setup(bot):
    bot.add_cog(general_cog(bot))