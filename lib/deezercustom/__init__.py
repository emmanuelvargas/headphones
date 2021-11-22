"""Python `Deezer API <http://developers.deezer.com/api>`_ Wrapper.

Implements several classes to interact with all types of Deezer objects,
do some searches, and build application written in Python on top of it

"""
from deezercustom.client import Client
from deezercustom.resources import Album, Resource, Artist, Playlist
from deezercustom.resources import Genre, Track, User, Comment, Radio


__version__ = "0.9.0"
__all__ = [
    "Client",
    "Resource",
    "Album",
    "Artist",
    "Genre",
    "Playlist",
    "Track",
    "User",
    "Comment",
    "Radio",
]
USER_AGENT = "Deezer Python API Wrapper v{0}".format(__version__)
