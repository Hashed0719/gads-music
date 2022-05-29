import discord
from discord import VoiceChannel, Guild
from discord.ext import commands

import wavelink
from wavelink import Node, Queue, QueueEmpty
from wavelink.utils import MISSING

import logging as log 

import random

import constants


class GPlayer(wavelink.Player):
    def __init__(self, client: discord.Client = MISSING, channel: VoiceChannel = MISSING, *, node: Node = MISSING):
        super().__init__(client, channel, node=node)
        self.psource = None
        self.text_channel = None
        self.queue_247 = Queue(max_size=10)
        self.is_playing_247 = False

    def __call__(self, client: commands.Bot, channel: VoiceChannel = MISSING):
        return super().__call__(client, channel)

    @property
    def is_playing(self):
        """is_connected and self.psource is not None"""
        return self.is_connected() and self.psource is not None

    async def play_247(self, node, playlist_urls):
        """Plays tracks from playlist urls passed."""
        if not self.is_playing_247:
            return

        if self.queue_247.is_empty:
            await self.fillqueue_247(node, playlist_urls)
        
        track = self.queue_247.get()
        await self.play(track)
        self.psource = track

    async def fillqueue_247(self, node, urls):
        """puts 10 songs in queue from playlists fetched from passed urls."""
        tracks = []
        for url in urls:
            playlist_obj :wavelink.YouTubePlaylist = await node.get_playlist(cls=wavelink.YouTubePlaylist, identifier=url)
            tracks.extend(playlist_obj.tracks)
        rand_tracks = random.choices(tracks, k=10)
        
        [self.queue_247.put(track) for track in rand_tracks]

    async def pplay(self, track):
        await self.play(track)
        self.psource = track
        self.is_playing_247 = False
    
    async def pskip(self):
        """Plays next song in queue and returns it. Raises `QueueEmpty` if queue.is_empty()"""
        next_track = self.queue.get()
        await self.play(next_track)
        self.psource = next_track
        return next_track

    async def pdisconnect(self):
        await self.disconnect(force=True)
        self.psource = None
        self.is_playing_247 = False

    async def pstop(self):
        await self.stop()
        self.psource = None
        self.is_playing_247 = False

        