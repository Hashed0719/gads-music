import discord 

from discord import SelectOption
from discord.ext import commands

from discord.commands.core import slash_command


class cogs_select(discord.ui.Select):
    def __init__(self, bot) -> None:
        self.bot = bot

        options = [SelectOption(label=ext_name) for ext_name in self.bot.extensions]

        super().__init__(
            custom_id="cogs restarter", 
            placeholder = "select cog to restart", 
            min_values = 1, 
            max_values = 1,
            options=options
        )
    
    async def callback(self, interaction):
        selected = self.values[0]
        self.bot.reload_extension(selected)
        await interaction.response.send_message(f"restarted **{self.values[0]}**", delete_after = 10)

class cogrestarter_view(discord.ui.View):   
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

        self.add_item(cogs_select(self.bot))    

class manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
    
    @commands.command(name="manager", aliases = ["manage", "mng"], hidden=True)
    async def manager(self, ctx :commands.Context):
        """sends a view to restart cog, helpful for letting user see the changes 
        without having the whole code to be restarted again."""
        view = cogrestarter_view(self.bot)
        await ctx.message.delete()
        await ctx.send("Cogs Restarter", view=view, delete_after=360)

    @slash_command()
    async def slash_check(self, ctx):
        """this is the docstring inside slashcheck command."""
        await ctx.respond("working fino!!")
        

def setup(bot):
    bot.add_cog(manager(bot))
    print(f"loaded {manager.__name__}")