import discord
from discord.ext import commands

import wavelink
from wavelink import YouTubePlaylist, QueueEmpty, LoadTrackError

import random, asyncio

import lavalink_server, constants
from membeds import MusicControlEmbeds as mcembeds


BOT_247_STATE = None       #Whether the bot is in 24/7 song playing mode.
PLAYLISTS = [
    "https://www.youtube.com/playlist?list=PLXTA_UaIstySqQZBGXbNOQ0aefumZF3-T",
    "https://www.youtube.com/playlist?list=PL2Zm_hoYG6LM-GSETav1ZVEz8jMz_8DXK",
    "https://www.youtube.com/playlist?list=PL9tY0BWXOZFvf-PV4_lnH3qSJ-jkAmY0G"
]


class GraciePlayer():
    """Music class to play songs 24/7."""

    def __init__(self, wavelink :wavelink):
        self.node: wavelink.Node= wavelink.NodePool.get_node(identifier="default-node")
        self.player: wavelink.Player= self.node.players[0]

    async def play_247(self):
        node = self.node
        player = self.node.players[0]
        
        try:
            playlist = []
            for yt_playlist in PLAYLISTS:
                try:
                    from_node = await node.get_playlist(cls=YouTubePlaylist, identifier=yt_playlist)
                except wavelink.errors.LavalinkException:
                    print("supressed wavelink.errors.LavalinkException")
                    continue    
                playlist.extend(from_node.tracks)
        except LoadTrackError:
            print("couldn't find playlist")

        playlist = random.choices(playlist, k=10)

        player.queue.extend(playlist)

        track = player.queue.get()
        await player.play(track)
        player.playing = track
        player.is_247 = True

    async def skip_track(self):
        player = self.player
        try:
            next_track = player.queue.get()
            player.playing = next_track
        except QueueEmpty:
            await self.play_247()


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
                                            https=True
                                            )
        except wavelink.errors.NodeOccupied:
            print(f"Node 'default-node' already exists! skipping node create...")


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

        if self.bot.voice_clients:
            await self.bot.voice_clients[0].disconnect(force=True)

        channel = await self.bot.fetch_channel(constants.ids.voice_channel_247)
        player = await channel.connect(cls=wavelink.Player)
        self.player = player

        gplayer = GraciePlayer(wavelink)
        await gplayer.play_247()
        BOT_247_STATE = True
    
    @commands.Cog.listener()
    async def on_wavelink_websocket_closed(self, player :wavelink.Player, reason, code):
        await player.disconnect(force=True)
        print(f"websocket close! player disconnected!, reason :{reason}, code:{code}")

        try:
            print("trying to connect node in <10> seconds.")
            await asyncio.sleep(10)
            await self.connect_nodes()
        except:
            print("couldn't connect node due to some error!")
        await GraciePlayer(wavelink).play_247()

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player, track: wavelink.Track):
        vc_text = self.bot.get_channel(constants.ids.vc_text)
        embed = mcembeds.playing(player, track)
        await vc_text.send(embed=embed, delete_after=track.length)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player :wavelink.Player, track, reason = None):
        if reason != "FINISHED":
            return
        try:
            track = player.queue.get()
            await player.play(track)
            player.playing = track
        except QueueEmpty:
            await GraciePlayer(wavelink).play_247()

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player: wavelink.Player, track, error):
        next_track = player.queue.get()
        await player.play(next_track)
        print(f"track skipped becuase of exception: {error}")

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, player: wavelink.Player, track: wavelink.Track, threshold=None):
        next_track = player.queue.get()
        await player.play(next_track)
        print(f"skipped {track.title} because of track stuck at threshold: {threshold}")

    @commands.command()
    async def start(self, ctx):
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client

        gplayer = GraciePlayer(wavelink)
        await gplayer.play_247()
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
            if player.is_247:
                player.queue.put_at_front(search)
                return
            else:
                player.queue.put(search)
                return

        await player.play(search)
        player.playing = search
        
    @commands.command()
    async def queue(self, ctx):
        player = wavelink.NodePool.get_node(identifier="default-node").players[0]
        await ctx.send(player.queue.count)

    @commands.command()
    async def skip(self, ctx):
        node = wavelink.NodePool.get_node(identifier="default-node")
        player = node.players[0]
        try:
            track = player.queue.get()
            await player.play(track)
            player.playing = track
            await ctx.send("skipped")
            return
        except QueueEmpty:
            await GraciePlayer(wavelink).play_247()
   
    @commands.command()
    async def stop(self, ctx):
        player = wavelink.NodePool.get_node(identifier="default-node").players[0]
        await player.stop()

    @commands.command()
    async def disconnect(self, ctx):
        player = wavelink.NodePool.get_node(identifier="default-node").players[0]
        await player.disconnect(force=True)
        await ctx.send("disconnected")

    @commands.command()
    async def check(self, ctx):
        node: wavelink.Node = wavelink.NodePool.get_node(identifier="default-node")
        print(node.players)
        print(node.identifier)
        player = node.get_player(constants.ids.guild_id)
        await ctx.send(player.is_connected())

def setup(bot):
    bot.add_cog(music_cog(bot))