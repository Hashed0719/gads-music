from turtle import title
import discord
from discord import Embed

class MusicControlEmbeds:
    """A class containing all the functions to create embeds for music playback."""
    
    def play(player, track) -> discord.Embed:
        embed = discord.Embed(
            # title=f"Now Playing...",
            description=f"[{track.title}]({track.uri})",
            color=discord.Colour.green()   
        )
        embed.set_author(name="Now Playing")

        if hasattr(player, "playing"):
            track = player.playing
            embed.set_thumbnail(url=track.thumbnail)
        
        return embed 

    def skip(player, track) -> discord.Embed:
        embed = discord.Embed(
            description=f"[{track.title}]({track.uri})",
            color=discord.Color.yellow()
        )
        embed.set_author(name="Skipped Song")
        
        if hasattr(player, "playing"):
            track = player.playing
            embed.set_thumbnail(url=track.thumbnail)

        return embed