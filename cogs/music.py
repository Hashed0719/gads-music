from tarfile import GNUTYPE_LONGLINK
import discord
from discord.ext import commands

import wavelink
from wavelink import YouTubePlaylist, QueueEmpty, LoadTrackError

import random, asyncio, logging as log

import lavalink_server, constants
# from membeds import MusicControlEmbeds as mcembeds, ControlView as cview
from gplayer import GPlayer
from membeds import MusicControlEmbeds as mcembeds


log.basicConfig(
    filename="data.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=log.INFO
)


BOT_247_STATE = None       #Whether the bot is in 24/7 song playing mode.
PLAYLISTS = constants.PLAYLISTS   

class music_cog(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.connect_nodes())

        self.node = None  #assigned on wavelink.node.ready
        self.player = None  #assigned on wavelink.node.ready
        self.is_247 = False

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

    
        try:
            await wavelink.NodePool.create_node(bot=self.bot,
                                            host=lavalink_server.HOST,
                                            port=lavalink_server.PORT,
                                            password=lavalink_server.PASSWORD,
                                            identifier="default-node",
                                            https=lavalink_server.HTTPS
                                            )
        except wavelink.errors.NodeOccupied:
            print(f"Node 'default-node' already exists! skipping node create...")
    
    async def ensure_voice(self, channel = None) -> GPlayer:
        if not self.bot.voice_clients:
            channel: discord.VoiceChannel = await self.bot.fetch_channel(constants.ids.voice_channel_247)
            player: GPlayer= await channel.connect(cls=GPlayer)
        else:
            player: GPlayer= self.bot.voice_clients[0]

        return player


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        log.info("invoked - wavelink - node ready event listener")
        """Event fired when a node has finished connecting."""
        self.node = node
        # await player.pdisconnect()
        print(f'Node: <{node.identifier}> is ready!')

        #starting 247
        player = await self.ensure_voice()
        channel = await self.bot.fetch_channel(constants.ids.vc_text)
        player.is_playing_247 = True
        player.text_channel = channel
        await player.play_247(node, PLAYLISTS)

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player :GPlayer, track :wavelink.Track):
        log.info("invoked - wavelink - track start event listener")
        channel :discord.TextChannel= player.text_channel
        if hasattr(player, "play_message"):
            message :discord.Message = player.play_message
            await message.edit(view=None)
        embed, view = mcembeds.play(player, track)
        player.play_message = await channel.send(embed=embed, view=view)
        
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: GPlayer, track: wavelink.Track, reason: str):
        log.info("invoked - wavelink - track end event listener")
        if reason == "REPLACED":
            embed = mcembeds.skip(player, track)
            channel = player.text_channel
            await channel.send(embed=embed)

        if reason == "FINISHED":
            if player.is_playing_247:
                await player.play_247(self.node, PLAYLISTS)
            else:
                try:
                    await player.pskip()
                except QueueEmpty:
                    player.is_playing_247 = True
                    await player.play_247(self.node, PLAYLISTS)

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *, track: wavelink.YouTubeTrack):
        """
        Plays specified songs form youtube.
        example:-`m.play gracie 21`
        """
        log.info("invoked - discord - play command")

        player: GPlayer = await self.ensure_voice()
        await player.pplay(track)
        player.text_channel = ctx.channel

    @commands.command(aliases=["s"])
    async def skip(self, ctx: commands.Context):
        """Skips the current playing song."""
        player: GPlayer= ctx.voice_client
        await player.pskip()
        
    @commands.command(aliases=["pn", "pnext"])
    async def playnext(self, ctx, *, track :wavelink.YouTubeTrack):
        """Queues the song to be played right next to the current playing song."""
        log.info("invoked - discord - playnext command")
        player = await self.ensure_voice()
        
        if player.is_playing():
            player.queue.put(track)
        else:
            await player.pplay(track)
        
    @commands.command(aliases=["dc"])
    async def disconnect(self, ctx):
        """Stop playing song and disconnect the player."""
        log.info("invoked - discord - disconnect command")
        player :GPlayer = await self.ensure_voice()
        await player.pdisconnect()


def setup(bot):
    bot.add_cog(music_cog(bot))