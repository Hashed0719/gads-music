from discord.ext import commands

import wavelink
from wavelink import YouTubePlaylist, QueueEmpty, LoadTrackError

import lavalink_server

import random


DEFAULT_MUSIC_CHANNEL_ID = 975312904444313610
BOT_247_STATE = None       #Whether the bot is in 24/7 song playing mode.
PLAYLISTS = [
    "https://www.youtube.com/playlist?list=PLXTA_UaIstySqQZBGXbNOQ0aefumZF3-T",
    "https://www.youtube.com/playlist?list=PL2Zm_hoYG6LM-GSETav1ZVEz8jMz_8DXK",
    "https://www.youtube.com/playlist?list=PL9tY0BWXOZFvf-PV4_lnH3qSJ-jkAmY0G"
]


class GraciePlayer():
    """Music class to play songs 24/7."""

    def __init__(self, wavelink :wavelink):
        self.node = wavelink.NodePool.get_node(identifier="default-node")

    async def play(self):
        node = self.node
        player = self.node.players[0]
        
        try:
            playlist = []
            for yt_playlist in PLAYLISTS:
                from_node = await node.get_playlist(cls=YouTubePlaylist, identifier=yt_playlist)
                playlist.extend(from_node.tracks)
        except LoadTrackError:
            print("couldn't find playlist")

        random.shuffle(playlist)

        player.queue.extend(playlist[0:10])

        track = player.queue.get()
        await player.play(track)


class membeds():
    pass


class music_cog(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

    
        await wavelink.NodePool.create_node(bot=self.bot,
                                            host=lavalink_server.HOST,
                                            port=lavalink_server.PORT,
                                            password=lavalink_server.PASSWORD,
                                            identifier="default-node",
                                            https=True
                                            )

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player :wavelink.Player, track, reason = None):
        if reason != "FINISHED":
            return
        try:
            track = player.queue.get()
            await player.play(track)
        except QueueEmpty:
            await GraciePlayer(wavelink).play()

    # @commands.command()
    # async def start(self, ctx: commands.Context):
    #     if not ctx.voice_client:
    #         pplayer :wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    #         self.pplayer = pplayer

    @commands.command()
    async def start(self, ctx):
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client

        gplayer = GraciePlayer(wavelink)
        await gplayer.play()
        BOT_247_STATE = True

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        """Play a song with the given search query.
        If not connected, connect to our voice channel.
        """
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client

        player.text_channel = ctx.channel

        if player.is_playing():
            player.queue.put(search)
        else:
            await player.play(search)
        
    @commands.command()
    async def queue(self, ctx):
        player = wavelink.NodePool.get_node(identifier="default-node").players[0]
        await ctx.send(player.queue.count)

    @commands.command()
    async def skip(self, ctx):
        player = wavelink.NodePool.get_node(identifier="default-node").players[0]
        try:
            track = player.queue.get()
            await player.play(track)
            await ctx.send("skipped")
            return
        except QueueEmpty:
            GraciePlayer(wavelink).play()
   

    @commands.command()
    async def stop(self, ctx):
        player = wavelink.NodePool.get_node(identifier="default-node").players[0]
        await player.stop()

    @commands.command()
    async def disconnect(self, ctx):
        player = wavelink.NodePool.get_node(identifier="default-node").players[0]
        await player.disconnect(force=True)
        await ctx.send("disconnected")



def setup(bot):
    bot.add_cog(music_cog(bot))