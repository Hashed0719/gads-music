from turtle import title
import discord
from discord import Embed

class MusicControlEmbeds:
    """A class containing all the functions to create embeds for music playback."""
    
    def playing(player, track) -> discord.Embed:
        embed = discord.Embed(
            # title=f"Now Playing...",
            description=f"[{track.title}]({track.uri})",
            color=discord.Colour.blurple()   
        )
        if hasattr(player, "playing"):
            track = player.playing
            embed.set_thumbnail(url=track.thumbnail)
        embed.set_author(name="Now Playing")
        
        return embed 