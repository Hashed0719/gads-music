import discord 

from discord import SlashCommand
from discord.ext import commands, pages


class customhelpcommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs = {"help":"Shows this command"})

    Command = commands.Command
    Cog = commands.Cog
    Page = pages.Page
    
    def make_pages(
        self, 
        cmdlist, 
        max_commands :int=7, 
        embed_color=discord.Colour.blurple()
    ):
        """
        Gets list of pages from command list, 
        having specified no. of max commands(default=7) per embed per page.
        """
        help_embeds = []
        embed = discord.Embed(title="Help")
        for no, command in enumerate(cmdlist,start=1):  
            embed.add_field(
                name=f"{command.name}",
                value=f"*{command.help}*",
                inline=False
            )
            if no%max_commands==0 or no==len(cmdlist):
                embed.color=embed_color
                help_embeds.append(embed)
                embed = discord.Embed(title="Help")    
    
        Page = pages.Page
        help_pages = [Page(embeds=[embed]) for embed in help_embeds]
        return help_pages

    def get_public_commands(self):
        """Returns list of  text commands which are not hidden."""
        bot :commands.Bot = self.context.bot
        textcommands = [command for command in bot.commands if not isinstance(command, SlashCommand)]
        public_commands = [command for command in textcommands if not command.hidden]
        return public_commands

    async def send_bot_help(self, mapping :dict):
        commands = self.get_public_commands()
        commands = await self.filter_commands(
            commands=commands, 
            sort=True, 
            key=lambda a: a.name
        )

        mypages = self.make_pages(commands)

        paginator = pages.Paginator(pages=mypages)

        channel = self.get_destination()
        await paginator.send(ctx=self.context ,target=channel)
        return await super().send_bot_help(mapping)


class help(commands.Cog):
    def __init__(self, bot :commands.Bot) -> None:
        self.bot = bot 
        self.oldhelpcommand = self.bot.help_command
        bot.help_command = customhelpcommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self.oldhelpcommand

def setup(bot):
    bot.add_cog(help(bot))